export async function sendKeypoints(keypoints: any[]) {
  // Format keypoints as needed for backend
  const formatted = keypoints.map(({ x, y, score, name }: any) => ({
    x, y, confidence: score, name
  }));
  try {
    await fetch("http://localhost:8000/pose-feedback-json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keypoints: formatted, user_id: "demo-user" }),
    });
  } catch (err) {
    // Optionally handle error
  }
} 