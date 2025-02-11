import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QComboBox
from bs4 import BeautifulSoup
from PyQt6.QtCore import QThread, pyqtSignal

class ParserThread(QThread):
    finished = pyqtSignal(str, object)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            self.finished.emit(html, soup)

        except requests.exceptions.RequestException as e:
            self.html_output.setText(f"Error: {e}")

class WebParserApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Parser")
        self.setGeometry(100,100,600,400)

        self.layout = QVBoxLayout()

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL")
        self.layout.addWidget(self.url_input)


        self.parse_button = QPushButton("Go!",self)
        self.parse_button.clicked.connect(self.start_parser)
        self.layout.addWidget(self.parse_button)

        self.html_output = QTextEdit(self)
        self.html_output.setReadOnly(True)
        self.layout.addWidget(self.html_output)

        self.tag_selector = QComboBox(self)
        self.tag_selector.addItems(["Все теги","div", "p", "span", "a","h1","h2","h3","ul","li"])
        self.tag_selector.currentIndexChanged.connect(self.update_class_list)
        self.layout.addWidget(self.tag_selector)


        self.class_selector = QComboBox(self)
        self.class_selector.currentIndexChanged.connect(self.filter_by_class)
        self.layout.addWidget(self.class_selector)

        self.filtred_output = QTextEdit(self)
        self.filtred_output.setReadOnly(True)
        self.layout.addWidget(self.filtred_output)

        self.setLayout(self.layout)
        self.parser_thread = None

    def start_parser(self):
        url = self.url_input.text()
        self.parse_button.setEnabled(False)
        self.html_output.setText("Загружаем сайт...")

        self.parser_thread = ParserThread(url)
        self.parser_thread.finished.connect(self.on_parsing_finished)
        self.parser_thread.start()

    def on_parsing_finished(self, html, soup):
        self.parse_button.setEnabled(True)
        self.html_output.setText(html if soup else html)
        if soup:
            self.soup = soup
            self.update_class_list()


    def update_class_list(self):
        selected_tag = self.tag_selector.currentText()
        class_set = set()
        if hasattr(self, 'soup'):
            if selected_tag == "Все теги":
                tags = self.soup.find_all(class_=True)
            else:
                tags = self.soup.find_all(selected_tag,class_=True)
                for tag in tags:
                    for cls in tag.get("class", []):
                        class_set.add(cls)

        self.class_selector.clear()
        self.class_selector.addItems(sorted(class_set))


    def filter_by_class(self):
        selected_class = self.class_selector.currentText()
        selected_tag = self.tag_selector.currentText()
        if hasattr(self, "soup"):
            if selected_tag == "Все теги":
                elements = self.soup.find_all(class_=selected_class)
            else:
                elements = self.soup.find_all(selected_tag,class_=selected_class)

            texts = [el.get_text(strip=True) for el in elements]
            self.filtred_output.setText("\n".join(texts) if texts else "None")

def main():
    app = QApplication(sys.argv)
    window = WebParserApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()