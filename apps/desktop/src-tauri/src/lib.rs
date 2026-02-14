use serde::Serialize;
use std::io::{Read, Write};
use tauri::{AppHandle, Emitter};
use tokio::net::TcpListener;

#[derive(Clone, Serialize)]
struct OAuthCallbackPayload {
    code: String,
}

/// Start a one-shot loopback HTTP listener for OAuth redirect.
/// Returns the port the listener is bound to.
#[tauri::command]
async fn start_oauth_listener(app: AppHandle) -> Result<u16, String> {
    let listener = TcpListener::bind("127.0.0.1:0")
        .await
        .map_err(|e| format!("Failed to bind listener: {e}"))?;

    let port = listener
        .local_addr()
        .map_err(|e| format!("Failed to get local addr: {e}"))?
        .port();

    // Spawn a task to handle exactly one connection
    tauri::async_runtime::spawn(async move {
        if let Ok((stream, _)) = listener.accept().await {
            // Wait for the stream to be readable
            if stream.readable().await.is_err() {
                return;
            }

            // Convert to std for synchronous read/write
            let std_stream = match stream.into_std() {
                Ok(s) => s,
                Err(_) => return,
            };

            let mut std_stream_clone = match std_stream.try_clone() {
                Ok(s) => s,
                Err(_) => return,
            };

            // Read the HTTP request
            let mut buf = [0u8; 4096];
            let n = match std_stream_clone.read(&mut buf) {
                Ok(n) => n,
                Err(_) => return,
            };
            let request = String::from_utf8_lossy(&buf[..n]);

            // Extract the code param from "GET /?code=...&... HTTP/1.1"
            let code = request
                .lines()
                .next()
                .and_then(|line| {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if parts.len() >= 2 {
                        Some(parts[1])
                    } else {
                        None
                    }
                })
                .and_then(|path| {
                    let full_url = format!("http://127.0.0.1{path}");
                    url::Url::parse(&full_url).ok()
                })
                .and_then(|parsed| {
                    parsed
                        .query_pairs()
                        .find(|(key, _)| key == "code")
                        .map(|(_, value)| value.into_owned())
                });

            // Send HTML response
            let (status, body) = if code.is_some() {
                (
                    "200 OK",
                    "<html><body style='font-family:system-ui;text-align:center;padding:60px;'>\
                     <h2>Sign-in successful!</h2>\
                     <p>You can close this tab and return to Mission Control.</p>\
                     </body></html>",
                )
            } else {
                (
                    "400 Bad Request",
                    "<html><body style='font-family:system-ui;text-align:center;padding:60px;'>\
                     <h2>Sign-in failed</h2>\
                     <p>No authorization code received. Please try again.</p>\
                     </body></html>",
                )
            };

            let response = format!(
                "HTTP/1.1 {status}\r\n\
                 Content-Type: text/html\r\n\
                 Content-Length: {}\r\n\
                 Connection: close\r\n\
                 \r\n\
                 {body}",
                body.len()
            );

            let _ = std_stream_clone.write_all(response.as_bytes());
            let _ = std_stream_clone.flush();

            // Emit the code back to the frontend
            if let Some(code) = code {
                let _ = app.emit("oauth-callback", OAuthCallbackPayload { code });
            }
        }
    });

    Ok(port)
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![start_oauth_listener])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
