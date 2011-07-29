# xVector Engine Client
# Copyright (c) 2011 James Buchwald

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

'''
Handles interactions with the metaserver.
'''

from .Retriever import Retriever
from .ui.MetaserverWidgetUI import Ui_MetaserverWidget
import tempfile
import os
import logging
import traceback
from xml.parsers import expat

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL

mainlog = logging.getLogger("Client.Main")

##
## Metaserver connection information
##
MetaserverHost = "localhost"
MetaserverPort = 8000
MetaserverURL = "/metaserver/fetch/"


class ServerRecord(object):
    '''
    Simple record of a server from the metaserver.
    '''
    def __init__(self):
        '''
        Creates an empty server record.
        '''
        # Declare attributes.
        self.Name = u""
        '''Name of the server.'''
        self.Description = u""
        '''Description of the server.'''
        self.Host = u""
        '''Hostname of the server.'''
        self.Port = 0
        '''Server port.'''
    
    def Complete(self):
        '''
        Determines if the record is complete.
        
        @return: Boolean value.
        '''
        return (bool(self.Name) and bool(self.Description) and bool(self.Host)
                and self.Port > 0 and self.Port < 65535)
    
    def __repr__(self):
        return "<ServerRecord: %s, %s, %s, %i>" % (self.Name, self.Description,
                                                   self.Host, self.Port)


class MetaserverDataError(Exception): pass
'''Raised if the metaserver supplies bad data.'''


class Metaclient(object):
    '''
    Asynchronous client for the metaserver.
    '''
    
    def __init__(self):
        '''
        Creates an empty client object.
        '''
        # Declare attributes.
        self.Servers = []
        '''List of servers, represented as ServerRecord objects.'''
        
        self.TempFile = None
        '''Filepath of the currently-used temporary file.'''
        
        self.RetrieverInstance = None
        '''Retriever instance '''
        
        self.Callback = None
        '''Optional callback from GetServers().'''
        
        self._CurrentServer = None
        '''Used by the XML parser when reading the server list.'''
        
        # Get our temporary file.
        self.TempFile = tempfile.mkstemp(prefix="xvector")[1]
    
    def _StartElementHandler(self, name, attributes):
        '''
        Expat callback called when an element is started.
        
        @type name: string
        @param name: Name of the element.
        
        @type attributes: dict
        @param attributes: Dict mapping attribute names to their string values.
        '''
        # is this a new server?
        if name.lower() == "server":
            # Start a new server record.
            self._CurrentServer = ServerRecord()
            self._CurrentServer.Name = attributes["Name"]
        
        # if not, is it a description?
        elif name.lower() == "info":
            self._CurrentServer.Description = attributes["Description"]
        
        # then is it connection information?
        elif name.lower() == "host":
            self._CurrentServer.Host = attributes["Address"]
            self._CurrentServer.Port = int(attributes["Port"])
    
    def _EndElementHandler(self, name):
        '''
        Expat callback called when an element is ended.
        
        @type name: string
        @param name: Name of the element.
        '''
        # is this the end of the server record?
        if name.lower() == "server":
            # Make sure the server record is complete.
            if not self._CurrentServer.Complete():
                raise MetaserverDataError
            self.Servers.append(self._CurrentServer)
            self._CurrentServer = None
    
    def _RetrieverCallback(self, code, crc):
        '''
        Callback from the retriever.
        
        @type code: integer
        @param code: Result code from the retriever.
        
        @type crc: string
        @param crc: CRC32 checksum of the retrieved file.
        '''
        # Any errors?
        if code != Retriever.Result_OK:
            # Failed.
            if self.Callback:
                self.Callback(code)
            return
        
        # Shut down the retriever.
        self.RetrieverInstance.Shutdown()
        
        # Try parsing the file.
        try:
            fileobj = file(self.TempFile, "r")
            parser = expat.ParserCreate()
            parser.StartElementHandler = self._StartElementHandler
            parser.EndElementHandler = self._EndElementHandler
            parser.ParseFile(fileobj)
        except:
            # failed, call the callback with an error code
            msg = "Error while parsing the metaserver data:\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
            if self.Callback:
                self.Callback(-1)
        finally:
            fileobj.close()
        
        # Call the callback.
        if self.Callback:
            self.Callback(code)
    
    def GetServers(self, callback_when_done=None):
        '''
        Gets the server list from the metaserver and reads it.
        
        This method is asynchronous and will return before completion.  An
        optional callback method can be provided that will be executed upon
        completion.  This method must take one argument, an integer result
        code which will be set to one of the constants in the Retriever class.
        
        @type callback_when_done: Callable object
        @param callback_when_done: Optional callback method called when the
        operation is completed (either successfully on unsuccessfully).
        '''
        # Spawn a retriever if needed.
        dirpart, filepart = os.path.split(self.TempFile)
        if not self.RetrieverInstance:
            self.RetrieverInstance = Retriever(MetaserverHost, MetaserverPort,
                                               dirpart)
        
        # Wipe the list, make the request.
        self.Servers = []
        self.Callback = callback_when_done
        self.RetrieverInstance.FetchResource(MetaserverURL, filepart,
                                             self._RetrieverCallback)
    
    def __del__(self):
        '''
        Called by Python immediately before the object is deleted.
        '''
        if self.TempFile:
            try:
                os.unlink(self.TempFile)
            except:
                msg = "Could not delete metaserver temporary file:\n"
                msg += traceback.format_exc()
                mainlog.error(msg)


##
## User interface for the metaserver
##

class MetaserverWidget(QtGui.QWidget):
    '''
    Provides a user interface to the metaserver.  Used on the startup screen.
    '''
    
    def __init__(self, parent=None):
        '''
        Creates a new metaserver widget.
        
        @type parent: QtGui.QWidget
        @param parent: Parent widget 
        '''
        # Inherit base class behavior.
        super(MetaserverWidget, self).__init__(parent)
        
        # Set up our UI.
        self.ui = Ui_MetaserverWidget()
        self.ui.setupUi(self)
        
        # Declare attributes.
        self.ListModel = None
        '''List model for the server list widget.'''
        self.Metaclient = None
        '''Metaserver client object.'''
        
        # Connect widgets.
        self.connect(self.ui.ServerList, SIGNAL("clicked(QModelIndex)"),
                     self.OnSelection)
        self.connect(self.ui.ConnectButton, SIGNAL("clicked()"),
                     self.OnConnect)
        self.connect(self.ui.BackButton, SIGNAL("clicked()"),
                     self.OnBack)
        
        # Fetch the metaserver information.
        try:
            self.Metaclient = Metaclient()
            self.Metaclient.GetServers(self._MetaserverCallback)
        except:
            msg = "Error while starting remote resource retriever.\n"
            msg += traceback.format_exc()
            mainlog.error(msg)
        
    def _MetaserverCallback(self, code):
        '''
        Callback passed to the Metaclient object.
        
        @type code: integer
        @param code: Result code
        '''
        # Did it work?
        if code != Retriever.Result_OK:
            # Something went wrong.
            msg = "Failed to retrieve public server list.\n"
            msg += "Error code %i." % code
            mainlog.error(msg)
            return
        
        # Update the server list.
        Servers = QtCore.QStringList()
        for entry in self.Metaclient.Servers:
            Servers.append(entry.Name)
        self.ListModel = QtGui.QStringListModel(Servers)
        self.ui.ServerList.setModel(self.ListModel)
    
    def OnConnect(self):
        '''
        Called when the user clicks Connect.
        '''
        # What are we connecting to?
        try:
            index = self.ui.ServerList.selectedIndexes()[0]
            server = self.Metaclient.Servers[index.row()]
        except:
            msg = "Invalid server selection."
            mainlog.error(msg)
            return
        
        # Connect
        address = (server.Host, server.Port)
        self.parent().ConnectToServer(address)
    
    def OnBack(self):
        '''
        Called when the user clicks Back.
        '''
        self.parent().BackToMain()
    
    def OnSelection(self, index):
        '''
        Called when the user selects a server from the list.
        
        @type index: QtCore.QModelIndex
        @param index: Selection index
        '''
        # What was selected?
        selected = self.Metaclient.Servers[index.row()]
        self.ui.DescriptionLabel.setText(selected.Description)
        
        # Enable the Connect button.
        self.ui.ConnectButton.setEnabled(True)
    
    def paintEvent(self, event):
        '''
        Called from Qt when the widget is repainted.
        
        @type event: QtGui.QPaintEvent
        @param event: Paint event
        '''
        # Enable stylesheets on this widget.
        opt = QtGui.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt,
                                   painter, self)
