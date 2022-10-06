
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
    document.getElementById(menuName).classList.remove('btn-outline-secondary');
    document.getElementById(menuName).classList.add('btn-outline-primary');
    document.getElementById(`${menuName}-rules`).style.display = "block";
}

function setSecondaryOutlineButton(menuName) {
    document.getElementById(menuName).classList.remove('btn-outline-primary');
    document.getElementById(menuName).classList.add('btn-outline-secondary');
    document.getElementById(`${menuName}-rules`).style.display = "none";
}

window.onload = function () {
    const rightMenuSelection = localStorage.getItem("right-menu-selection");
    const ruleSelection = localStorage.getItem("rule-selection");
    if (rightMenuSelection == "rules") {
        setPrimaryButton("rules")
        setSecondaryButton("help")
    }
    else if (rightMenuSelection == "help") {
        setPrimaryButton("help")
        setSecondaryButton("rules")
    }

    if (ruleSelection == "TFL") {
        setPrimaryOutlineButton("TFL");
        setSecondaryOutlineButton("FOL");
    }
    else if (ruleSelection == "FOL") {
        setPrimaryOutlineButton("FOL");
        setSecondaryOutlineButton("TFL");
    }
};

function showInformation(e) {
    var button = document.getElementById(e);
    if (e == "rules") {
        setPrimaryButton("rules")
        setSecondaryButton("help")
        localStorage.setItem("right-menu-selection", "rules");
    }
    else if (e == 'help') {
        setPrimaryButton("help")
        setSecondaryButton("rules")
        localStorage.setItem("right-menu-selection", "help");
    }
}

function showRules(e) {
    if (e === "TFL") {
        setPrimaryOutlineButton("TFL");
        setSecondaryOutlineButton("FOL");
        localStorage.setItem("rule-selection", "TFL");
    }
    else if (e === "FOL") {
        setPrimaryOutlineButton("FOL");
        setSecondaryOutlineButton("TFL");
        localStorage.setItem("rule-selection", "FOL");
    }
}