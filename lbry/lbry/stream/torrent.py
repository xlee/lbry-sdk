import asyncio
import logging

log = logging.getLogger(__name__)


class Torrent:
    def __init__(self, loop, handle):
        self._loop = loop
        self._handle = handle
        self.finished = asyncio.Event(loop=loop)

    def _threaded_update_status(self):
        status = self._handle.status()
        if not status.is_seeding:
            log.info('%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
                status.progress * 100, status.download_rate / 1000, status.upload_rate / 1000,
                status.num_peers, status.state))
        elif not self.finished.is_set():
            self.finished.set()

    async def wait_for_finished(self):
        while True:
            await self._loop.run_in_executor(
                None, self._threaded_update_status
            )
            if self.finished.is_set():
                log.info("finished downloading torrent!")
                await self.pause()
                break
            await asyncio.sleep(1, loop=self._loop)

    async def pause(self):
        log.info("pause torrent")
        await self._loop.run_in_executor(
            None, self._handle.pause
        )

    async def resume(self):
        await self._loop.run_in_executor(
            None, self._handle.resume
        )
