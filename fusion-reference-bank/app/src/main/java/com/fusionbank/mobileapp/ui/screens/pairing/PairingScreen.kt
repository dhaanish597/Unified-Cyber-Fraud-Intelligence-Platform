package com.fusionbank.mobileapp.ui.screens.pairing

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.fusionbank.mobileapp.sdk.Fusion
import com.fusionbank.mobileapp.ui.theme.*

@Composable
fun PairingScreen(onPaired: () -> Unit) {
    val context = LocalContext.current
    var payload by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    Box(Modifier.fillMaxSize().background(PrimaryDark).padding(24.dp), contentAlignment = Alignment.Center) {
        Column(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Default.QrCodeScanner, contentDescription = "Pairing QR", tint = AccentCyan, modifier = Modifier.size(64.dp))
            Text("FUSION RISK OS", color = TextPrimaryDark, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            Text("Pair this APK with the Developer Portal", color = TextSecondaryDark)
            Spacer(Modifier.height(24.dp))
            OutlinedTextField(
                value = payload,
                onValueChange = { payload = it },
                label = { Text("Paste pairing QR payload") },
                placeholder = { Text("{ backend, ws, pairId, bootstrapToken, expires }") },
                minLines = 4,
                modifier = Modifier.fillMaxWidth(),
            )
            error?.let { Text(it, color = StatusRed, modifier = Modifier.padding(top = 8.dp)) }
            Spacer(Modifier.height(16.dp))
            Button(
                enabled = payload.isNotBlank() && !busy,
                onClick = {
                    busy = true; error = null
                    Fusion.pair(context, payload, onResult = { result ->
                        busy = false
                        result.onSuccess { onPaired() }.onFailure { error = it.message ?: "Pairing failed" }
                    })
                },
                modifier = Modifier.fillMaxWidth(),
            ) { if (busy) CircularProgressIndicator(Modifier.size(20.dp)) else Text("PAIR DEVICE") }
            Spacer(Modifier.height(10.dp))
            Text("Scan support can paste the decoded QR JSON here; no source or URL changes are required.", color = TextSecondaryDark, style = MaterialTheme.typography.bodySmall)
        }
    }
}
