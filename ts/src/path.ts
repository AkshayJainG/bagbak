const SEP = '/'

export function relativeTo(base: string, full: string) {
  const a = normalize(base).split(SEP)
  const b = normalize(full).split(SEP)

  let i = 0;
  while (a[i] === b[i])
    i++
  return b.slice(i).join(SEP)
}

export function normalize(path: string) {
  return ObjC.classes.NSString.stringWithString_(path)
    .stringByStandardizingPath().toString()
}

export function rstrip(path: string) {
  return path.replace(/\/$/, '')
}

export function join() {
  return [].map.call(arguments, rstrip).join(SEP)
}

export function basename(path: string) {
  return ObjC.classes.NSString.stringWithString_(path)
    .lastPathComponent().toString()
}