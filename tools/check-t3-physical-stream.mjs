// Exercise the installed router's real default-selection path without a phone.
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";

const modulePath = process.argv[2];
if (!modulePath) throw new Error("Usage: node tools/check-t3-physical-stream.mjs <middleware.js>");
const { createRouter } = await import(pathToFileURL(modulePath).href);
for (const [serial, expectedMode] of [
  ["shutrwise-test-phone", "scrcpy"],
  ["emulator-5554", "grpc-screenshot"],
]) {
  let selected;
  const router = createRouter({ streamMode: "grpc-screenshot" }, {
    listDevices: async () => [{ serial }],
    createApp: async (options) => {
      selected = options;
      throw new Error("Stop at the capture boundary; no device access in this test.");
    },
  });
  try {
    await router.handleRequest(new Request(
      `http://localhost/api/stream-mode?device=${serial}`,
    ));
    assert.equal(selected?.streamMode, expectedMode);
    if (expectedMode === "scrcpy") assert.equal(selected.inputSource, "scrcpy");
    console.log(`PASS: ${serial} defaults to ${expectedMode}`);
  } finally {
    await router.stopAll();
  }
}
