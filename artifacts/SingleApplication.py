# https://gist.github.com/teionn/186d1730f7dcffc4e97cb14e67f829d6

from PySide2.QtWidgets import QWidget
import sys
from PySide2.QtCore import Signal, QTextStream, Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtNetwork import QLocalSocket, QLocalServer

from win32gui import SetWindowPos
import win32con

# https://stackoverflow.com/questions/12712360/qtsingleapplication-for-pyside-or-pyqt
# https://stackoverflow.com/questions/12118939/how-to-make-a-pyqt4-window-jump-to-the-front


class SingleApplication(QApplication):

    messageReceived = Signal()

    def __init__(self, id, *argv):

        super(SingleApplication, self).__init__(*argv)
        self._id = id
        self._activationWindow = None
        self._activateOnMessage = False

        # Is there another instance running?
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self._id)
        self._isRunning = self._outSocket.waitForConnected()

        if self._isRunning:
            # Yes, there is.
            self._outStream = QTextStream(self._outSocket)
            self._outStream.setCodec('UTF-8')
        else:
            # No, there isn't.
            self._outSocket = None
            self._outStream = None
            self._inSocket = None
            self._inStream = None
            self._server = QLocalServer()
            self._server.listen(self._id)
            self._server.newConnection.connect(self._onNewConnection)

    def isRunning(self):
        return self._isRunning

    def id(self):
        return self._id

    def activationWindow(self):
        return self._activationWindow

    def setActivationWindow(self, activationWindow, activateOnMessage=True):
        self._activationWindow = activationWindow
        self._activateOnMessage = activateOnMessage

    def activateWindow(self):

        if not self._activationWindow:
            return

        self._activationWindow.show()

        self._activationWindow.setWindowState(
            (self._activationWindow.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)

        SetWindowPos(self._activationWindow.winId(),
                     # = always on top. only reliable way to bring it to the front on windows
                     win32con.HWND_TOPMOST,
                     0, 0, 0, 0,
                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

        # Do not reset topmost; for monitor control this is set...
        # SetWindowPos(self._activationWindow.winId(),
        #             # disable the always on top, but leave window at its top position
        #             win32con.HWND_NOTOPMOST,
        #             0, 0, 0, 0,
        #             win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

        # self._activationWindow.raise_()
        self._activationWindow.activateWindow()

    def sendMessage(self, msg):
        if not self._outStream:
            return False
        self._outStream << msg << '\n'
        self._outStream.flush()
        return self._outSocket.waitForBytesWritten()

    def _onNewConnection(self):
        if self._inSocket:
            self._inSocket.readyRead.disconnect(self._onReadyRead)
        self._inSocket = self._server.nextPendingConnection()
        if not self._inSocket:
            return
        self._inStream = QTextStream(self._inSocket)
        self._inStream.setCodec('UTF-8')
        self._inSocket.readyRead.connect(self._onReadyRead)
        if self._activateOnMessage:
            self.activateWindow()

    def _onReadyRead(self):
        while True:
            msg = self._inStream.readLine()
            if not msg:
                break
            self.messageReceived.emit(msg)


if __name__ == '__main__':

    appGuid = 'B0EFFF-B0EF-B0EF-B0EF-B0EFB0EFB0EF'
    app = SingleApplication(appGuid, sys.argv)
    if app.isRunning():
        print("The window is already displayed.")
        sys.exit(0)

    w = QWidget()
    w.show()
    app.setActivationWindow(w)
    sys.exit(app.exec_())
