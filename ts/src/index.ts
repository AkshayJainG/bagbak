import { ping, kickstart } from './extensions'
import { pull } from './transfer';


function ready() {
  const p = Module.findExportByName(null, 'dlopen') as NativePointerValue;
  const dlopen = new NativeFunction(p, 'pointer', ['pointer', 'int']);
  dlopen(Memory.allocUtf8String('/System/Library/Frameworks/Foundation.framework/Foundation'), 0);
}

ready();




rpc.exports = {
  decrypt() {
    // todo
  },
  pull,
  ping,
  kickstart,
}