const { NSExtension, NSString } = ObjC.classes

export function ping() {
  ObjC.classes.NSExtension.extensionWithIdentifier_error_('com.apple.nonexist', NULL)
}

export function kickstart(id) {
  const identifier = NSString.stringWithString_(id)
  const extension = NSExtension.extensionWithIdentifier_error_(identifier, NULL)
  if (!extension)
    throw new Error('unable to create extension ' + id)

  const pid = extension['- _plugInProcessIdentifier']()
  if (pid)
    return Promise.resolve(pid)

  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      const pid = extension['- _plugInProcessIdentifier']()
      if (pid)
        resolve(pid)
      else
        reject('unable to get extension pid')
    }, 400)

    extension.beginExtensionRequestWithInputItems_completion_(NULL, new ObjC.Block({
      retType: 'void',
      argTypes: ['object'],
      implementation(requestIdentifier) {
        clearTimeout(timeout)
        const pid = extension.pidForRequestIdentifier_(requestIdentifier)
        resolve(pid)
      }
    }))
  })
}