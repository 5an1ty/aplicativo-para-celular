package com.megabrain.bobsnake;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.*;
import java.io.ByteArrayInputStream;

public final class MainActivity extends Activity {
    private WebView web;
    private View fullscreen;
    private WebChromeClient.CustomViewCallback fullscreenCallback;
    private static final String ORIGIN = "https://game.local/";
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(0xff05293f);
        getWindow().setNavigationBarColor(0xff05293f);
        web = new WebView(this);
        web.setBackgroundColor(0xff05293f);
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setSupportZoom(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !request.getUrl().toString().startsWith(ORIGIN);
            }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (url.startsWith(ORIGIN)) {
                    String path = request.getUrl().getPath();
                    if (path == null || path.equals("/")) path = "/index.html";
                    if (!path.contains("..")) try {
                        String mime = path.endsWith(".html") ? "text/html" : path.endsWith(".js") ? "application/javascript" : path.endsWith(".css") ? "text/css" : path.endsWith(".mp3") ? "audio/mpeg" : path.endsWith(".svg") ? "image/svg+xml" : path.endsWith(".png") ? "image/png" : path.endsWith(".ttf") ? "font/ttf" : "application/octet-stream";
                        return new WebResourceResponse(mime, path.endsWith(".mp3") ? null : "UTF-8", getAssets().open("game" + path));
                    } catch (java.io.IOException ignored) {}
                }
                return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", java.util.Collections.emptyMap(), new ByteArrayInputStream(new byte[0]));
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public void onShowCustomView(View view, CustomViewCallback callback) {
                if (fullscreen != null) { callback.onCustomViewHidden(); return; }
                fullscreen = view; fullscreenCallback = callback;
                ((ViewGroup)getWindow().getDecorView()).addView(view, new ViewGroup.LayoutParams(-1,-1));
            }
            @Override public void onHideCustomView() { hideFullscreen(); }
        });
        setContentView(web);
        immersive();
        web.loadUrl(ORIGIN);
    }
    private void immersive() {
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }
    private void hideFullscreen() {
        if (fullscreen == null) return;
        ((ViewGroup)getWindow().getDecorView()).removeView(fullscreen);
        fullscreen = null;
        if (fullscreenCallback != null) fullscreenCallback.onCustomViewHidden();
        fullscreenCallback = null;
        immersive();
    }
    @Override public void onWindowFocusChanged(boolean focused) { super.onWindowFocusChanged(focused); if (focused) immersive(); }
    @Override protected void onPause() {
        web.evaluateJavascript("if(typeof paused!=='undefined' && typeof over!=='undefined' && !paused && !over && !document.getElementById('game').classList.contains('hidden')) togglePause();", null);
        web.onPause(); super.onPause();
    }
    @Override protected void onResume() { super.onResume(); if (web != null) web.onResume(); }
    @Override public void onBackPressed() {
        if (fullscreen != null) { hideFullscreen(); return; }
        web.evaluateJavascript("(function(){if(!document.getElementById('game').classList.contains('hidden')){if(!paused && !over)togglePause();else goMenu();return true;}return false;})()", value -> {
            if ("false".equals(value)) new AlertDialog.Builder(this).setTitle("Sair do jogo?").setPositiveButton("Sair", (dialog, which) -> finish()).setNegativeButton("Continuar", null).show();
        });
    }
    @Override protected void onDestroy() { web.destroy(); super.onDestroy(); }
}
