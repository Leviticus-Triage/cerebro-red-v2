# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]: "[plugin:vite:esbuild] Transform failed with 1 error: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/src/pages/ExperimentMonitor.tsx:768:7: ERROR: Multiple exports with the same name \"default\""
  - generic [ref=e5]: /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/src/pages/ExperimentMonitor.tsx:749:0
  - generic [ref=e6]: "Multiple exports with the same name \"default\" 766| export default ExperimentMonitor; 767| 768| export default ExperimentMonitor;var _c;$RefreshReg$(_c, \"ExperimentMonitor\"); | ^ 769| 770| if (import.meta.hot && !inWebWorker) {"
  - generic [ref=e7]: at failureErrorWithLog (/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/node_modules/esbuild/lib/main.js:1467:15) at /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/node_modules/esbuild/lib/main.js:736:50 at responseCallbacks.<computed> (/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/node_modules/esbuild/lib/main.js:603:9) at handleIncomingPacket (/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/node_modules/esbuild/lib/main.js:658:12) at Socket.readFromStdout (/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/frontend/node_modules/esbuild/lib/main.js:581:7) at Socket.emit (node:events:524:28) at addChunk (node:internal/streams/readable:561:12) at readableAddChunkPushByteMode (node:internal/streams/readable:512:3) at Readable.push (node:internal/streams/readable:392:5) at Pipe.onStreamRead (node:internal/stream_base_commons:191:23
  - generic [ref=e8]:
    - text: Click outside, press Esc key, or fix the code to dismiss.
    - text: You can also disable this overlay by setting
    - code [ref=e9]: server.hmr.overlay
    - text: to
    - code [ref=e10]: "false"
    - text: in
    - code [ref=e11]: vite.config.ts
    - text: .
```