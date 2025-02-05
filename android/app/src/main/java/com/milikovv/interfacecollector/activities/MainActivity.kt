package com.milikovv.interfacecollector.activities

import android.media.projection.MediaProjectionConfig
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.milikovv.interfacecollector.suppliers.media_projection.MediaProjectionService
import com.milikovv.interfacecollector.ui.theme.InterfaceCollectorTheme


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            InterfaceCollectorTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Greeting(
                            name = "Android",
                            modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }

        //val intent = Intent(applicationContext, OverlayService::class.java)
        //if (applicationContext != null) {
        //    applicationContext.startService(intent)
        //}

        //val intent = Intent(applicationContext, Multiplexer::class.java)
        //applicationContext.startService(intent)

        initMediaProjection()
    }

    private fun initMediaProjection() {
        val mediaProjectionManager = getSystemService(MediaProjectionManager::class.java)

        val startMediaProjection = registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) { result ->
            if (result.resultCode == RESULT_OK) {
                // After obtaining permission
                val intent = MediaProjectionService.newIntent(this, result.resultCode, result.data)
                startService(intent)
            }
        }

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startMediaProjection.launch(mediaProjectionManager.createScreenCaptureIntent())
        } else {
            // Disable "single window" option
            startMediaProjection.launch(mediaProjectionManager.createScreenCaptureIntent(
                MediaProjectionConfig.createConfigForDefaultDisplay()))
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    InterfaceCollectorTheme {
        Greeting("Android")
    }
}