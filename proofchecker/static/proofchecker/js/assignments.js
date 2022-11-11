document.addEventListener('DOMContentLoaded', resetError, false);

function add_problem() {
    requiredFieldCheck()
    document.getElementById('hx-btn').click();
    setTimeout(() => {
    }, 200);
}

function mutate(mutations) {
    window.location = "/problems/add?assignment=" + target.innerText
}

var target = document.querySelector('div#returnValue')
var observer = new MutationObserver(mutate);
var config = {characterData: false, attributes: false, childList: true, subtree: false};

observer.observe(target, config);



function resetError() {
    $('#id_errorResponseMain').addClass("hidden");
    $('#id_errorResponse').text('');
}


function requiredFieldCheck() {
    const timeout = 3000;
    resetError();
    if ($('#id_title').val() === '') {
        $('#id_errorResponse').text("Please add a Title to this assignment to proceed. Title, Course, Start Date, and Due Date are required fields.");
        $("#id_errorResponseMain").show();
        setTimeout(function() { $("#id_errorResponseMain").hide(); }, timeout);
        return
    }
    if ($('#id_course').val() === '') {
        $('#id_errorResponse').text("Please add a Course to this assignment to proceed. Title, Course, Start Date, and Due Date are required fields.");
        $("#id_errorResponseMain").show();
        setTimeout(function() { $("#id_errorResponseMain").hide(); }, timeout);
        return
    }
    if ($('#id_start_date').val() === '') {
        $('#id_errorResponse').text("Please add a Start Date to this assignment to proceed. Title, Course, Start Date, and Due Date are required fields.");
        $("#id_errorResponseMain").show();
        setTimeout(function() { $("#id_errorResponseMain").hide(); }, timeout);
        return
    }
    if ($('#id_due_by').val() === '') {
        $('#id_errorResponse').text("Please add a Due Date to this assignment to proceed. Title, Course, Start Date, and Due Date are required fields.");
        $("#id_errorResponseMain").show();
        setTimeout(function() { $("#id_errorResponseMain").hide(); }, timeout);
        return
    }
    resetError();
}