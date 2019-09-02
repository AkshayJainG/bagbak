#!/usr/bin/env python3
# encoding: utf-8


import codecs
import tempfile
import os
import sys
import shutil
import frida



from recv import FileReceiver


def fatal(reason):
    print(reason)
    sys.exit(-1)


def find_app(app_name_or_id, device_id, device_ip):
    if device_id is None:
        if device_ip is None:
            dev = frida.get_usb_device()
        else:
            frida.get_device_manager().add_remote_device(device_ip)
            dev = frida.get_device("tcp@" + device_ip)
    else:
        try:
            dev = next(dev for dev in frida.enumerate_devices()
                       if dev.id.startswith(device_id))
        except StopIteration:
            fatal('device id %s not found' % device_id)

    if dev.type not in ('tether', 'remote', 'usb'):
        fatal('unable to find device')

    try:
        app = next(app for app in dev.enumerate_applications() if
                   app_name_or_id == app.identifier or
                   app_name_or_id == app.name)
    except:
        print('app "%s" not found' % app_name_or_id)
        print('installed app:')
        for app in dev.enumerate_applications():
            print('%s (%s)' % (app.name, app.identifier))
        fatal('')

    return dev, app

def on_console(level, text):
    print('[%s] %s' % (level, text))


def main():
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--device', nargs='?', help='device id (prefix)')
    # parser.add_argument('--ip', nargs='?', help='ip to connect over network')
    # parser.add_argument('app', help='application name or bundle id')
    # parser.add_argument('-o', '--output', help='output filename')
    # parser.add_argument('-v', '--verbose', help='verbose mode', action='store_true')
    # parser.add_argument('--keep-watch', action='store_true',
    #                     default=False, help='preserve WatchOS app'),
    # parser.add_argument('--skip-plugins', action='store_true',
    #                     default=False, help='skip app plugins')
    # args = parser.parse_args()


    # dev, app = find_app(args.app, args.device, args.ip)

    # task = IPADump(dev, app,
    #                keep_watch=args.keep_watch,
    #                output=args.output,
    #                verbose=args.verbose,
    #                skip_plugins=args.skip_plugins)
    # task.run()

    dev = frida.get_usb_device()
    for app in dev.enumerate_applications():
        if app.name == 'WeChat':
            # print(app.pid)
            # return
            session = dev.attach(app.pid)
            test(session)


def test(session):
    agent = os.path.join('ts', 'dist.js')
    with codecs.open(agent, 'r', 'utf-8') as fp:
        agent_source = fp.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        script = session.create_script(agent_source)
        script.on('message', on_message)
        script.set_log_handler(on_console)
        FileReceiver(script, tmpdir).connect()
        script.load()
        script.exports.pull()
        session.detach()

        print(tmpdir)
        input()
    

def on_message(msg, data):
    print(msg)

if __name__ == '__main__':
    main()
