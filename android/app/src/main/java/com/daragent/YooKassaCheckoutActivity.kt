package com.daragent

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView

class YooKassaCheckoutActivity : ComponentActivity() {
    private var checkoutUrl: String? = null
    private var returnUrl: String? = null

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        checkoutUrl = intent.getStringExtra("checkout_url")
        returnUrl = intent.getStringExtra("return_url")

        setContent {
            CheckoutScreen(
                url = checkoutUrl,
                returnUrl = returnUrl,
                onCompleted = { finish() }
            )
        }
    }
}

@Composable
fun CheckoutScreen(url: String?, returnUrl: String?, onCompleted: () -> Unit) {
    if (url == null) {
        onCompleted()
        return
    }

    AndroidView(
        modifier = Modifier.fillMaxSize(),
        factory = { context ->
            WebView(context).apply {
                webViewClient = object : WebViewClient() {
                    override fun onPageCommitVisible(view: WebView, url: String) {
                        if (returnUrl != null && url.startsWith(returnUrl)) {
                            onCompleted()
                        }
                    }

                    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                        val requestUrl = request.url.toString()
                        if (returnUrl != null && requestUrl.startsWith(returnUrl)) {
                            onCompleted()
                            return true
                        }
                        return false
                    }
                }
                webChromeClient = WebChromeClient()
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.loadWithOverviewMode = true
                loadUrl(url)
            }
        }
    )
}
