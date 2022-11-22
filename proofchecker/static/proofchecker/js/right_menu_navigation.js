function setPrimaryButton(menuName) {
    document.getElementById(menuName).classList.remove('btn-secondary');
    document.getElementById(menuName).classList.add('btn-primary');
    document.getElementById(`${menuName}-information`).style.display = "block";
}

function setSecondaryButton(menuName) {
    document.getElementById(menuName).classList.remove('btn-primary');
    document.getElementById(menuName).classList.add('btn-secondary');
    document.getElementById(`${menuName}-information`).style.display = "none";
}

function setPrimaryOutlineButton(menuName) {
    document.getElementById(menuName).classList.remove('btn-secondary');
    document.getElementById(menuName).classList.add('btn-primary');
    document.getElementById(`${menuName}-rules`).style.display = "block";
}

function setSecondaryOutlineButton(menuName) {
    document.getElementById(menuName).classList.remove('btn-primary');
    document.getElementById(menuName).classList.add('btn-secondary');
    document.getElementById(`${menuName}-rules`).style.display = "none";
}



function showInformation(e) {

    if (e == "rules") {
        setPrimaryButton("rules")
        setSecondaryButton("help")

    } else if (e == 'help') {
        setPrimaryButton("help")
        setSecondaryButton("rules")

    }
}

function showRules(e) {
    if (e === "TFL") {
        setPrimaryOutlineButton("TFL");
        setSecondaryOutlineButton("FOL");

    } else if (e === "FOL") {
        setPrimaryOutlineButton("FOL");
        setSecondaryOutlineButton("TFL");

    }
}

