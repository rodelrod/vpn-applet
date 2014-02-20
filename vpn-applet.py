#!/usr/bin/env python
"""VPN applet to connect to Rueil L2TP/IPSec VPN"""
import sys
import time
import gtk
import appindicator
import envoy
import pynotify
from os.path import dirname, realpath

SDIR = dirname(realpath(__file__))
APPNAME = "VPN Applet"

class VpnApplet:

    def __init__(self):
        self.ind = appindicator.Indicator("vpn-applet",
                                          "vpn-applet",
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("new-messages-red")
        self._menu_setup()
        self.ind.set_menu(self.menu)

    def _menu_setup(self):
        self.menu = gtk.Menu()

        self.connect_item = gtk.MenuItem("Connect to Rueil")
        self.connect_item.connect("activate", self.connect)
        self.menu.append(self.connect_item)

        self.disconnect_item = gtk.MenuItem("Disconnect from Rueil")
        self.disconnect_item.connect("activate", self.disconnect)
        self.menu.append(self.disconnect_item)


        # check if we're connected already
        check_connected = envoy.run("ip address | grep ppp0")
        if check_connected.std_out:
            # we're already connected
            self.disconnect_item.show()
        else:
            self.connect_item.show()

        self.separator = gtk.SeparatorMenuItem()
        self.separator.show()
        self.menu.append(self.separator)

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.notification_is_set = pynotify.init("vpn-applet")
        gtk.main()

    def connect(self, widget):
        connect_process = envoy.run("gksudo " + SDIR + "/connect_rueil.sh")
        if connect_process.status_code == 0:
            check_connected = envoy.run("ip address | grep ppp0")
            if check_connected.std_out:
                self._toggle_menu(connected=True)
                if self.notification_is_set:
                    self._notify('connected')
            else:
                self._toggle_menu(connected=False)
                self._notify('error_connect')
        else:
            self._toggle_menu(connected=False)
            if self.notification_is_set:
                self._notify('error_connect')
           
    def disconnect(self, widget):
        disconnect_process = envoy.run("gksudo " + SDIR + "/disconnect_rueil.sh")
        if disconnect_process.status_code == 0:
            self._toggle_menu(connected=False)
            if self.notification_is_set:
                self._notify('disconnected')
        else:
            check_connected = envoy.run("ip address | grep ppp0")
            if check_connected.std_out:
                self._toggle_menu(connected=False)
                if self.notification_is_set:
                    self._notify('disconnected')
            else:
                self._toggle_menu(connected=True)
                if self.notification_is_set:
                    self._notify('error_disconnect')

    def quit(self, widget):
        sys.exit(0)

    def _notify(self, status):
        if status == 'error_connect':
            message = ("Error connecting to Rueil VPN: "
                       "check syslog and auth.log")
        elif status == 'error_disconnect':
            message = ("Error disconnecting from Rueil VPN: "
                       "check syslog and auth.log")
        elif status == 'connected':
            message = "Successfully connected to Rueil VPN"
        elif status == 'disconnected':
            message = "Successfully disconnected from Rueil VPN"
        else:
            message = "Unidentified status"
        n = pynotify.Notification(APPNAME, message)
        n.show()

    def _toggle_menu(self, connected=False):
        if connected:
            self.connect_item.hide()
            self.disconnect_item.show()
        else:
            self.connect_item.show()
            self.disconnect_item.hide()



if __name__ == "__main__":
    indicator = VpnApplet()
    indicator.main()
