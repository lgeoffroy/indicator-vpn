#!/usr/bin/env python3
# coding: utf-8
# author: lgeoffroy

import gi
import os
import re
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib

ICONPATH = os.path.dirname(os.path.realpath(__file__)) + '/icons/'

class IndicatorVpn:
    def __init__(self):
        self.ind = appindicator.Indicator.new(
                    'NordVPN',
                    ICONPATH + 'disconnected.png',
                    appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.menu = Gtk.Menu()

        self.state = 'Disconnected'
        self.status_menu = Gtk.MenuItem()
        self.status_menu.set_label('Status: Disconnected')
        self.status_menu.set_sensitive(False)
        self.menu.append(self.status_menu)

        item = Gtk.SeparatorMenuItem()
        self.menu.append(item)

        self.connect_menu = Gtk.MenuItem()
        self.connect_menu.set_label('Connect')
        self.connect_menu.connect('activate', self.connect)
        self.menu.append(self.connect_menu)

        self.disconnect_menu = Gtk.MenuItem()
        self.disconnect_menu.set_label('Disconnect')
        self.disconnect_menu.set_sensitive(False)
        self.disconnect_menu.connect('activate', self.disconnect)
        self.menu.append(self.disconnect_menu)

        item = Gtk.SeparatorMenuItem()
        self.menu.append(item)

        item = Gtk.MenuItem()
        item.set_label('Exit')
        item.connect('activate', self.quit)
        self.menu.append(item)

        self.menu.show_all()
        self.ind.set_menu(self.menu)

    def main(self):
        self.check_status()
        GLib.timeout_add(1000, self.check_status)
        Gtk.main()

    def set_icon(self, icon):
        self.ind.set_icon(ICONPATH + icon)

    def transform_output(self, output):
        return re.sub('[-/\\|]', '', output.stdout.decode('utf-8')).strip(' \t\n\r')

    def send_notification(self, text):
        subprocess.run(['notify-send', '-i', ICONPATH + 'nordvpn.png', '-t', '2000', 'NordVPN', text])

    def check_status(self):
        status = self.transform_output(subprocess.run(['nordvpn', 'status'], stdout=subprocess.PIPE))
        self.status_menu.set_label(status)
        state = status.split('\n')[0].split(':')[1].strip()
        if state != self.state:
            self.set_icon('connected.png' if state == 'Connected' else 'disconnected.png')
            self.connect_menu.set_sensitive(False if state == 'Connected' else True)
            self.disconnect_menu.set_sensitive(True if state == 'Connected' else False)
            self.state = state
        return True

    def connect(self, widget):
        self.status_menu.set_label('Connecting...')
        result = subprocess.run(['nordvpn', 'c'], stdout=subprocess.PIPE)
        text = self.transform_output(result).split('\n')[1]
        self.send_notification(text)
        self.set_icon('connected.png')

    def disconnect(self, widget):
        self.status_menu.set_label('Disconnecting...')
        result = subprocess.run(['nordvpn', 'd'], stdout=subprocess.PIPE)
        text = self.transform_output(result)
        self.send_notification(text)
        self.set_icon('disconnected.png')

    def quit(self, widget):
        Gtk.main_quit()

if __name__ == '__main__':
  indicator = IndicatorVpn();
  indicator.main();
