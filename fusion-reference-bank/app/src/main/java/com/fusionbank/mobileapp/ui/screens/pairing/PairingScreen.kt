package com.fusionbank.mobileapp.ui.screens.pairing

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.sdk.security.SecureStorage
import com.fusionbank.mobileapp.ui.theme.*
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions

@Composable
fun PairingScreen(
    onPaired: () -> Unit,
    onSkip: (() -> Unit)? = null      // If already paired, skip directly to login
) {
    val context = LocalContext.current
    var payload by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var success by remember { mutableStateOf(false) }
    var showManual by remember { mutableStateOf(false) }

    // Animated scan ring
    val infiniteTransition = rememberInfiniteTransition(label = "scan_ring")
    val scanAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(900, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scan_alpha"
    )

    val qrScanLauncher = rememberLauncherForActivityResult(
        contract = ScanContract(),
        onResult = { result ->
            val value = result.contents
            if (!value.isNullOrBlank()) {
                payload = value
                busy = true
                error = null
                Fusion.pair(context, value, onResult = { pairResult ->
                    busy = false
                    if (pairResult.isSuccess) {
                        success = true
                    } else {
                        error = pairResult.exceptionOrNull()?.message
                            ?.replace(Regex("HTTP\\s*[45]\\d{2}"), "the server response")
                            ?: "Pairing could not be completed. Check that the QR code is valid and retry."
                    }
                })
            }
        }
    )

    // After showing success briefly, navigate
    LaunchedEffect(success) {
        if (success) {
            kotlinx.coroutines.delay(1200)
            onPaired()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(PrimaryDark)
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // ── Brand ─────────────────────────────────────────────────────
            Text(
                text = "FUZEN AI",
                color = PrimaryBlue,
                fontWeight = FontWeight.Black,
                fontSize = 22.sp,
                letterSpacing = 4.sp
            )
            Text(
                text = "Device Pairing",
                color = TextSecondaryDark,
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(bottom = 32.dp)
            )

            // ── QR Scanner Icon / Success State ───────────────────────────
            if (success) {
                Icon(
                    imageVector = Icons.Default.CheckCircle,
                    contentDescription = "Paired",
                    tint = Color(0xFF10B981),
                    modifier = Modifier.size(80.dp)
                )
                Spacer(Modifier.height(12.dp))
                Text("Device Paired!", color = Color(0xFF10B981), fontWeight = FontWeight.Bold, fontSize = 18.sp)
                Text("Establishing secure session…", color = TextSecondaryDark, style = MaterialTheme.typography.bodySmall)
            } else {
                // Animated QR target
                Box(
                    modifier = Modifier
                        .size(140.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(SurfaceDark)
                        .border(
                            width = (2.5 * scanAlpha).dp,
                            color = AccentCyan.copy(alpha = scanAlpha),
                            shape = RoundedCornerShape(16.dp)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.QrCodeScanner,
                        contentDescription = "QR Scanner",
                        tint = AccentCyan.copy(alpha = scanAlpha),
                        modifier = Modifier.size(72.dp)
                    )
                }
            }

            Spacer(Modifier.height(28.dp))

            if (!success) {
                // ── Main Scan Button ─────────────────────────────────────
                Button(
                    onClick = {
                        error = null
                        val options = ScanOptions().apply {
                            setDesiredBarcodeFormats(ScanOptions.QR_CODE)
                            setPrompt("Point camera at Fuzen AI pairing QR code")
                            setCameraId(0)
                            setBeepEnabled(false)
                            setBarcodeImageEnabled(false)
                            setOrientationLocked(false)
                        }
                        qrScanLauncher.launch(options)
                    },
                    enabled = !busy,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = AccentCyan,
                        contentColor = PrimaryDark
                    ),
                    modifier = Modifier.fillMaxWidth().height(52.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    if (busy) {
                        CircularProgressIndicator(Modifier.size(22.dp), color = PrimaryDark, strokeWidth = 2.5.dp)
                    } else {
                        Icon(Icons.Default.QrCodeScanner, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(10.dp))
                        Text("SCAN PAIRING QR CODE", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    }
                }

                Spacer(Modifier.height(12.dp))

                // ── Manual entry toggle ──────────────────────────────────
                TextButton(onClick = { showManual = !showManual }) {
                    Text(
                        if (showManual) "Hide manual entry" else "Or enter payload manually",
                        color = TextSecondaryDark,
                        style = MaterialTheme.typography.bodySmall
                    )
                }

                if (showManual) {
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = payload,
                        onValueChange = { payload = it },
                        label = { Text("Paste pairing QR payload (JSON)") },
                        placeholder = { Text("{ \"backend\":\"…\", \"ws\":\"…\", \"pairId\":\"…\" }") },
                        minLines = 3,
                        maxLines = 6,
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = AccentCyan,
                            unfocusedBorderColor = CardBorderDark
                        )
                    )
                    Spacer(Modifier.height(10.dp))
                    Button(
                        enabled = payload.isNotBlank() && !busy,
                        onClick = {
                            busy = true
                            error = null
                            Fusion.pair(context, payload, onResult = { pairResult ->
                                busy = false
                                if (pairResult.isSuccess) success = true
                                else error = pairResult.exceptionOrNull()?.message
                                    ?.replace(Regex("HTTP\\s*[45]\\d{2}"), "the server response")
                                    ?: "Pairing could not be completed. Check the payload and retry."
                            })
                        },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        if (busy) CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp)
                        else Text("PAIR DEVICE MANUALLY", fontWeight = FontWeight.Bold)
                    }
                }

                // Error display
                error?.let { err ->
                    Spacer(Modifier.height(12.dp))
                    Card(
                        colors = CardDefaults.cardColors(containerColor = StatusRed.copy(alpha = 0.12f)),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = err,
                            color = StatusRed,
                            modifier = Modifier.padding(12.dp),
                            style = MaterialTheme.typography.bodySmall,
                            textAlign = TextAlign.Center
                        )
                    }
                }

                Spacer(Modifier.height(24.dp))

                // ── Skip button (if already paired) ─────────────────────
                if (onSkip != null) {
                    OutlinedButton(
                        onClick = onSkip,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = TextSecondaryDark)
                    ) {
                        Text("Already paired? Reconnect")
                        Spacer(Modifier.width(6.dp))
                        Icon(Icons.Default.ArrowForward, contentDescription = null, modifier = Modifier.size(16.dp))
                    }
                }

                Spacer(Modifier.height(16.dp))
                Text(
                    text = "Scan the QR code from your Fuzen AI Developer Portal to pair this device to the platform.",
                    color = TextSecondaryDark,
                    style = MaterialTheme.typography.labelSmall,
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}
