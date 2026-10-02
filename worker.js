// Preserve the original customer link while serving the shared portfolio.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === 'starminer-public.tanshuai.workers.dev' &&
        (url.pathname === '/' || url.pathname === '/index.html')) {
      return Response.redirect('https://work.tanshuai.com/starminer/desk-miner-101/', 301);
    }
    return env.ASSETS.fetch(request);
  },
};
