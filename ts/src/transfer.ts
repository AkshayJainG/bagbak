import fs from 'fs';
import path from 'path';


interface PullOption {
  verbose?: boolean,
  iWatch?: boolean,
}

export async function pull(opt: PullOption = {}) {
  const { NSFileManager, NSBundle } = ObjC.classes;
  const root = NSBundle.mainBundle().bundlePath().toString();
  console.log('root:', root);
  const fileMgr = NSFileManager.defaultManager();
  const enumerator = fileMgr.enumeratorAtPath_(root);
  let nextObj = null;
  while ((nextObj = enumerator.nextObject()), nextObj) {
    const relative = nextObj.toString();
    if (/(\_CodeSignature\/CodeResources|SC_Info\/\w+\.s(inf|upf|upp|upx))$/.test(relative))
      continue;

    if (!opt.iWatch && /^Watch\//.test(relative))
      continue;

    if (opt.verbose)
      console.log('send:', relative)

    try {
      await transfer(root, relative);
    } catch(e) {
      if (!/(\/Plugins\/(.*)\.appex\/)?SC_Info\//.test(relative))
          console.warn(`unable to open ${relative} (${e.message})`)
        continue
    }
  }

  enumerator.release();
}

export async function transfer(root: string, relative: string) {
  const session = Math.random().toString(36).substr(2);
  const highWaterMark = 16 * 1024 * 1024;
  const subject = 'download';
  const absolute = path.join(root, relative);
  const { mode, size } = fs.statSync(absolute);

  if (mode & fs.constants.S_IFDIR) {
    send({
      subject,
      event: 'mkdir',
      relative,
    });
    return false;
  }
  
  if (!(mode & fs.constants.S_IFREG)) {
    console.error('unknown file mode', absolute);
    return false;
  }

  const filename = path.join(root, relative);
  const stream = fs.createReadStream(filename, { highWaterMark });

  send({
    subject,
    event: 'start',
    relative,
    session,
    size,
  });

  recv('ack', () => { }).wait();
  const format = (size: number) => `${(size / 1024 / 1024).toFixed(2)}MiB`;

  let sent = 0;
  await new Promise((resolve, reject) =>
    stream
      .on('data', chunk => {
        send({
          subject,
          event: 'data',
          session,
        }, chunk)

        recv('flush', () => { }).wait()
        sent += chunk.byteLength
        console.log(`downloaded ${format(sent)} of ${format(size)}, ${(sent * 100 / size).toFixed(2)}%`)
      })
      .on('end', resolve)
      .on('error', reject));

  send({
    subject,
    event: 'end',
    session,
  })

  console.log('transfer complete');
  return true;
}