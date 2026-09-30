package com.fusionbank.mobileapp.ui.screens.safecheck

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.models.SafeCheckResponse
import com.fusionbank.mobileapp.ui.theme.*
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions

private const val MAX_SCAN_PAYLOAD = 4096
private const val DUPLICATE_SCAN_WINDOW_MS = 3_000L

private data class SafeCheckDraft(
    val payload: String,
    val qrType: String,
    val payeeAddress: String? = null,
    val encodedName: String? = null,
    val amount: String? = null,
    val currency: String? = null,
    val host: String? = null,
)

private fun parseForReview(raw: String): Result<SafeCheckDraft> {
    val payload = raw.trim()
    if (payload.isEmpty()) return Result.failure(IllegalArgumentException("QR payload is empty."))
    if (payload.length > MAX_SCAN_PAYLOAD) return Result.failure(IllegalArgumentException("QR payload is too large to analyze."))

    val scheme = payload.substringBefore(":", "").lowercase()
    if (scheme.isNotEmpty() && scheme !in setOf("upi", "http", "https")) {
        return Result.failure(IllegalArgumentException("This QR uses an unsupported or unsafe URI scheme."))
    }

    return try {
        if (payload.startsWith("upi://pay", ignoreCase = true) ||
            Regex("(?:^|[?&])pa=", RegexOption.IGNORE_CASE).containsMatchIn(payload)
        ) {
            val uri = Uri.parse(payload)
            val payee = uri.getQueryParameter("pa")?.trim()
            if (payee.isNullOrBlank()) {
                Result.failure(IllegalArgumentException("UPI QR has no payment identifier."))
            } else {
                Result.success(
                    SafeCheckDraft(
                        payload = payload,
                        qrType = "UPI-style QR",
                        payeeAddress = payee,
                        encodedName = uri.getQueryParameter("pn")?.trim()?.takeIf { it.isNotEmpty() },
                        amount = uri.getQueryParameter("am")?.trim()?.takeIf { it.isNotEmpty() },
                        currency = uri.getQueryParameter("cu")?.trim()?.takeIf { it.isNotEmpty() },
                    )
                )
            }
        } else if (scheme == "http" || scheme == "https") {
            val uri = Uri.parse(payload)
            val host = uri.host?.trim()
            if (host.isNullOrBlank()) {
                Result.failure(IllegalArgumentException("URL QR has no valid destination host."))
            } else {
                Result.success(SafeCheckDraft(payload = payload, qrType = "Web URL QR", host = host))
            }
        } else {
            Result.success(SafeCheckDraft(payload = payload, qrType = "Unsupported QR format"))
        }
    } catch (_: Exception) {
        Result.failure(IllegalArgumentException("QR payload is malformed or cannot be decoded."))
    }
}

private fun openAppSettings(context: Context) {
    context.startActivity(
        Intent(
            Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
            Uri.parse("package:${context.packageName}"),
        )
    )
}

@Composable
fun SafeCheckScreen() {
    val context = LocalContext.current
    var draft by remember { mutableStateOf<SafeCheckDraft?>(null) }
    var assessment by remember { mutableStateOf<SafeCheckResponse?>(null) }
    var busy by remember { mutableStateOf(false) }
    var scanning by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var permissionDenied by remember { mutableStateOf(false) }
    var lastScanFingerprint by remember { mutableStateOf<String?>(null) }
    var lastScanAt by remember { mutableLongStateOf(0L) }
    var reportOpen by remember { mutableStateOf(false) }
    var category by remember { mutableStateOf("scam") }
    var description by remember { mutableStateOf("") }
    var reportMessage by remember { mutableStateOf<String?>(null) }

    fun analyze(value: String) {
        busy = true
        error = null
        reportMessage = null
        Fusion.analyzeSafeCheck(value) { result ->
            busy = false
            result.fold(
                onSuccess = { assessment = it },
                onFailure = { error = it.message ?: "SafeCheck is unavailable. Retry when connected." },
            )
        }
    }

    val scanner = rememberLauncherForActivityResult(ScanContract()) { result ->
        scanning = false
        val contents = result.contents?.trim()
        if (contents.isNullOrBlank()) {
            error = "No QR was captured. Point the camera at a QR and try again."
            return@rememberLauncherForActivityResult
        }
        val now = System.currentTimeMillis()
        val fingerprint = contents.hashCode().toString()
        if (fingerprint == lastScanFingerprint && now - lastScanAt < DUPLICATE_SCAN_WINDOW_MS) {
            error = "This QR was already captured. Review it or scan a different QR."
            return@rememberLauncherForActivityResult
        }
        lastScanFingerprint = fingerprint
        lastScanAt = now
        parseForReview(contents).fold(
            onSuccess = {
                draft = it
                assessment = null
                error = null
            },
            onFailure = { error = it.message ?: "This QR could not be safely parsed." },
        )
    }

    fun launchScanner() {
        scanning = true
        scanner.launch(
            ScanOptions().apply {
                setDesiredBarcodeFormats(ScanOptions.QR_CODE)
                setPrompt("Scan a payment or web QR")
                setBeepEnabled(false)
                setBarcodeImageEnabled(false)
                setOrientationLocked(false)
                setTimeout(30_000L)
            }
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        permissionDenied = !granted
        if (granted) launchScanner()
        else error = "Camera permission is required to scan a QR. You can allow it and retry."
    }

    fun openScanner() {
        error = null
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            launchScanner()
        } else {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().background(RrrBackground).verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Text("Fusion SafeCheck", color = RrrTextPrimary, fontSize = 26.sp, fontWeight = FontWeight.Black)
        Text(
            "Scan a QR to review observable risk signals before you pay. SafeCheck never executes payments.",
            color = RrrTextMuted,
            style = MaterialTheme.typography.bodyMedium,
        )

        Button(
            onClick = ::openScanner,
            enabled = !busy && !scanning,
            modifier = Modifier.fillMaxWidth().height(54.dp),
            colors = ButtonDefaults.buttonColors(containerColor = RrrCyan, contentColor = RrrBackground),
            shape = RoundedCornerShape(12.dp),
        ) {
            if (scanning) CircularProgressIndicator(Modifier.size(22.dp), color = RrrBackground, strokeWidth = 2.dp)
            else {
                Icon(Icons.Default.QrCodeScanner, contentDescription = null)
                Spacer(Modifier.width(10.dp))
                Text("SCAN QR FOR SAFECHECK", fontWeight = FontWeight.Bold)
            }
        }

        if (permissionDenied) {
            Card(colors = CardDefaults.cardColors(containerColor = StatusYellow.copy(alpha = .12f))) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Camera permission denied", color = StatusYellow, fontWeight = FontWeight.Bold)
                    Text("Allow camera access to scan a real QR. If Android has blocked the permission, enable it in app settings.", color = RrrTextMuted, style = MaterialTheme.typography.bodySmall)
                    if (context is Activity) {
                        TextButton(onClick = { openAppSettings(context) }) { Text("OPEN APP SETTINGS", color = RrrCyan) }
                    }
                }
            }
        }

        error?.let {
            Card(colors = CardDefaults.cardColors(containerColor = StatusRed.copy(alpha = .12f))) {
                Row(Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.ErrorOutline, contentDescription = null, tint = StatusRed)
                    Spacer(Modifier.width(8.dp))
                    Text(it, color = StatusRed, style = MaterialTheme.typography.bodySmall)
                }
            }
        }

        draft?.let { captured ->
            Card(colors = CardDefaults.cardColors(containerColor = RrrSurface), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("PAYMENT IDENTIFIER", color = RrrTextMuted, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    DetailRow("Source", captured.qrType)
                    captured.encodedName?.let { DetailRow("Name encoded in QR", it) }
                    captured.payeeAddress?.let { DetailRow("Payment identifier", it) }
                    captured.host?.let { DetailRow("URL host", it) }
                    DetailRow("Amount", captured.amount?.let { "${captured.currency ?: ""} $it" } ?: "Not specified")
                    Text("Captured payload is treated as untrusted input and will not be opened or executed.", color = RrrTextMuted, style = MaterialTheme.typography.labelSmall)
                    Button(onClick = { analyze(captured.payload) }, enabled = !busy, modifier = Modifier.fillMaxWidth()) {
                        Text(if (busy) "ANALYZING…" else "ANALYZE RISK")
                    }
                }
            }
        }

        assessment?.let { result ->
            val riskColor = when (result.riskLevel) {
                "HIGH" -> StatusRed
                "MEDIUM" -> StatusYellow
                "LOW" -> StatusGreen
                else -> RrrTextMuted
            }
            val displayLevel = if (result.riskLevel == "MEDIUM") "ELEVATED" else result.riskLevel
            Card(colors = CardDefaults.cardColors(containerColor = RrrSurface), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("FUSION SAFETY ASSESSMENT", color = RrrTextMuted, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                        Column {
                            Text(result.riskScore?.let { "$it / 100" } ?: "Not established", color = riskColor, fontSize = 28.sp, fontWeight = FontWeight.Black)
                            Text("$displayLevel OBSERVED RISK", color = riskColor, fontWeight = FontWeight.Bold)
                        }
                        Text("${result.confidence}%\nconfidence", color = RrrTextPrimary, textAlign = TextAlign.End)
                    }
                    Text("QR TYPE: ${result.qrType}", color = RrrTextMuted, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    result.parsedDetails.encodedPayeeName?.let { DetailRow("Name encoded in QR", it) }
                    result.parsedDetails.payeeAddress?.let { DetailRow("UPI ID", it) }
                    result.parsedDetails.amount?.let { DetailRow("Amount", "${result.parsedDetails.currency ?: ""} $it") }
                    result.parsedDetails.host?.let { DetailRow("Host", it) }
                    Text("WHY?", color = RrrTextPrimary, fontWeight = FontWeight.Bold)
                    result.signals.take(6).forEach { signal ->
                        Text("• ${signal.message}", color = if (signal.severity == "HIGH") StatusRed else RrrTextMuted, style = MaterialTheme.typography.bodySmall)
                    }
                    Text(result.recommendation, color = RrrTextPrimary, fontWeight = FontWeight.SemiBold)
                    Text("Identity verification data unavailable; an encoded name is not independent verification.", color = StatusYellow, style = MaterialTheme.typography.labelSmall)
                    TextButton(onClick = { reportOpen = !reportOpen }) { Text("REPORT SUSPICIOUS PAYMENT", color = RrrCyan) }
                }
            }
        }

        if (reportOpen && assessment != null) {
            val identifier = assessment!!.parsedDetails.payeeAddress ?: assessment!!.parsedDetails.url ?: assessment!!.parsedDetails.host
            Card(colors = CardDefaults.cardColors(containerColor = RrrSurface), shape = RoundedCornerShape(14.dp)) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("REPORT SUSPICIOUS PAYMENT", color = RrrTextPrimary, fontWeight = FontWeight.Bold)
                    Text("Your report will be reviewed. Do not include passwords, OTPs, PINs, CVVs, or banking credentials.", color = RrrTextMuted, style = MaterialTheme.typography.bodySmall)
                    OutlinedTextField(value = category, onValueChange = { category = it }, label = { Text("Category") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                    OutlinedTextField(value = description, onValueChange = { description = it }, label = { Text("What looked suspicious?") }, minLines = 3, modifier = Modifier.fillMaxWidth())
                    Button(
                        enabled = !identifier.isNullOrBlank() && description.trim().length >= 3,
                        onClick = {
                            Fusion.reportSafeCheck(identifier!!, category.trim(), description.trim()) { report ->
                                report.fold(
                                    onSuccess = { reportMessage = it.message; reportOpen = false },
                                    onFailure = { reportMessage = it.message ?: "Report could not be submitted." },
                                )
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("SUBMIT REPORT") }
                }
            }
        }
        reportMessage?.let { Text(it, color = StatusGreen, style = MaterialTheme.typography.bodySmall) }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = RrrCyan, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(6.dp))
            Text("Intelligence only — confirm recipient details in your banking app.", color = RrrTextMuted, style = MaterialTheme.typography.labelSmall)
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, color = RrrTextMuted, style = MaterialTheme.typography.bodySmall)
        Text(value, color = RrrTextPrimary, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
    }
}
