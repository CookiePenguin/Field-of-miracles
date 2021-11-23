import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtGui import QPainter, QColor
from random import randint, choice
from random import randint as gen


class Circles(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.col = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Brown', 'Black']

    def initUI(self):
        self.setWindowTitle("жёлтые круги")
        self.butt = QPushButton(self)
        self.butt.setGeometry(350, 350, 200, 200)
        self.butt.setText('нажми')
        self.butt.clicked.connect(self.draw_flag)
        self.flag = False
        self.show()

    def draw_flag(self):
        self.flag = True
        if self.flag:
            self.repaint()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        if self.flag:
            x, y = gen(0, self.width() - 1), gen(0, self.height() - 1)
            qp.setBrush(QColor(choice(self.col)))
            qp.drawEllipse(x, y, randint(1, 450), randint(1, 450))
            self.flag = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Circles()
    ex.show()
    exit(app.exec())
