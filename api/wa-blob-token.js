// Lets the /wa-upload/ page put a big photo/video/file straight into Vercel Blob (no 4.5 MB website limit).
// Only for a valid one-time 📎 link from the CEO Dashboard (HubSpot task WAUPLOAD + random key).
const { checkUploadTask } = require('./_wa');

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'method' });
  if (!process.env.BLOB_READ_WRITE_TOKEN) return res.status(503).json({ error: 'no storage' });
  const { handleUpload } = require('@vercel/blob/client');
  try {
    const out = await handleUpload({
      body: req.body, request: req,
      onBeforeGenerateToken: async (pathname, clientPayload) => {
        let p = {}; try { p = JSON.parse(clientPayload || '{}'); } catch (e) {}
        const ok = await checkUploadTask(p.task, p.key);
        if (ok.error) throw new Error(ok.error);
        if (!/^wa\/out\//.test(pathname)) throw new Error('bad path');
        return { addRandomSuffix: true, maximumSizeInBytes: 100 * 1024 * 1024, validUntil: Date.now() + 30 * 60e3 };
      },
      onUploadCompleted: async () => {}
    });
    return res.status(200).json(out);
  } catch (e) { return res.status(400).json({ error: String(e.message || e).slice(0, 160) }); }
};
