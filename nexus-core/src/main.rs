use axum::{
    routing::{get, post},
    Json, Router,
    extract::State,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use std::time::{SystemTime, UNIX_EPOCH};
use futures::future::join_all;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Target {
    url: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct InterceptedData {
    id: String,
    title: String,
    #[serde(alias = "estimated_retail_value")]
    shadow_price: f64,
    #[serde(alias = "roi_percentage")]
    roi_percentage: f64,
    #[serde(default)]
    entropy_level: f64,
    #[serde(default)]
    momentum: f64,
    #[serde(default)]
    timestamp: u64,
    #[serde(alias = "max_bid")]
    max_bid: f64,
}

struct AppState {
    client: reqwest::Client,
}

const PYTHON_BACKEND: &str = "http://127.0.0.1:8000";

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::fmt::layer())
        .init();

    let state = Arc::new(AppState {
        client: reqwest::Client::builder()
            .user_agent("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
            .pool_max_idle_per_host(20)
            .build()
            .unwrap(),
    });

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/v1/intercept", post(initiate_intercept))
        .route("/api/v1/batch_intercept", post(batch_intercept))
        .with_state(state)
        .layer(CorsLayer::permissive());

    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    tracing::info!("AGENTI Core: Sovereign Interceptor active on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_check() -> &'static str {
    "AGENTI: Sovereign Core Online"
}

async fn initiate_intercept(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<Target>
) -> Json<Vec<InterceptedData>> {
    tracing::info!("Ghost-Proxy: Relaying Intercept to Scraper Rail -> {}", payload.url);

    let response = state.client
        .post(format!("{}/api/v1/intercept", PYTHON_BACKEND))
        .json(&payload)
        .send()
        .await;

    match response {
        Ok(res) => {
            if let Ok(mut items) = res.json::<Vec<InterceptedData>>().await {
                let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
                for item in items.iter_mut() {
                    item.timestamp = now;
                    // Random entropy for visual jitter if not provided by scraper
                    if item.entropy_level == 0.0 {
                        item.entropy_level = (now % 100) as f64 / 100.0;
                    }
                    if item.momentum == 0.0 {
                        item.momentum = (now % 50) as f64 / 10.0;
                    }
                }
                Json(items)
            } else {
                Json(vec![])
            }
        },
        Err(_) => Json(vec![])
    }
}

async fn batch_intercept(
    State(state): State<Arc<AppState>>,
    Json(payloads): Json<Vec<Target>>
) -> Json<Vec<InterceptedData>> {
    tracing::info!("Ghost-Batch: Orchestrating {} simultaneous intercepts", payloads.len());

    let futures = payloads.into_iter().map(|target| {
        let state_clone = state.clone();
        tokio::spawn(async move {
            let res = initiate_intercept(State(state_clone), Json(target)).await;
            res.0
        })
    });

    let results = join_all(futures).await;
    let flattened: Vec<InterceptedData> = results.into_iter()
        .filter_map(|r| r.ok())
        .flatten()
        .collect();

    Json(flattened)
}
