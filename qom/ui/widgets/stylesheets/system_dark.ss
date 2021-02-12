QWidget {
    background-color: #212121;
    border: 0px solid #212121;
    color: #EEEEEE;
    margin: 0px 32px;
}

QCheckBox {
    font-size: 10pt;
    color: #EEEEEE;
    spacing: 8px;
}

QCheckBox::indicator:unchecked {
    background-color: #212121;
    border: 2px solid #373737;
}

QCheckBox::indicator:unchecked:hover {
    border: 2px solid #424242;
}

QCheckBox::indicator:unchecked:pressed {
    background-color: #4D4D4D;
}

QCheckBox::indicator:checked {
    background-color: #4D4D4D;
    border: 2px solid #373737;
}

QCheckBox::indicator:checked:hover {
    border: 2px solid #424242;
}

QCheckBox::indicator:checked:pressed {
    background-color: #212121;
}

QComboBox {
    background-color: #2C2C2C;
    border: 0px solid #2C2C2C;
    padding: 0px 8px;
    font-size: 10pt;
    color: #EEEEEE;
    margin: 0px;
}

QComboBox:hover {
    background-color: #373737;
}

QComboBox::drop-down {
    background-color: #373737;
    border: 0px solid #373737;
    color: #EEEEEE;
}

QComboBox QAbstractItemView {
    background-color: #2C2C2C;
    selection-color: #EEEEEE;
    selection-background-color: #373737;
    outline: 0px solid #373737;
    margin: 0px;
}

QPushButton {
    background-color: #2C2C2C;
    border: 0px solid #2C2C2C;
    font-size: 10pt;
    color: #EEEEEE;
    margin: 0px;
}

QPushButton:hover {
    background-color: #373737;
}