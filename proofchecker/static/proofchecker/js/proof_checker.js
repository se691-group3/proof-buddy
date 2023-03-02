// ---------------------------------------------------------------------------------------------------------------------
// list of variables  to store dom element ids/classes/names (difference between inlineformset vs modelformset
// ---------------------------------------------------------------------------------------------------------------------
const FORMSET_PREFIX = "proofline_set";                         // for modelformset - "form-"
const FORMSET_TOTALFORMS_ID = "id_proofline_set-TOTAL_FORMS";   // for modelformset - "id_form-TOTAL_FORMS"
const FORMSET_INITIALLFORMS_ID = "id_proofline_set-INITIAL_FORMS";   // for modelformset - "id_form-INITIAL_FORMS"
const FORMSET_TBODY_ID = "proofline-list";                      // for modelformset - "proofline-list"
const FORMSET_TR_CLASS = "proofline_set";                       // for modelformset - "proofline-form"

// ---------------------------------------------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', reload_page, false);

// ---------------------------------------------------------------------------------------------------------------------
// functions
// ---------------------------------------------------------------------------------------------------------------------
/**
 * this function will run once DOM contents are loaded
 */
function reload_page() {
    //this function will run on page load
    updateLineCount()

    //will sort proof table based on ORDER field
    sort_table()
    //will decide which button to display between start and restart
    set_start_restart_at_beginning()

    update_comment_response_button()

    //Decide if we should display the table
    set_table_visibility()

    hide_make_parent_button()
    update_row_indentations()
    updateLineCount()

}


// Downlaod button
window.onload = function () {
    document.getElementById("download")
        .addEventListener("click", () => {
            const form = this.document.getElementById("proof_form");
            var opt = {
                margin: .25,
                filename: `${this.document.getElementById("id_name").value.replace(" ", "_")}.pdf`,
                image: {type: 'jpeg', quality: 0.98},
                html2canvas: {scale: 1},
                jsPDF: {unit: 'in', format: 'letter', orientation: 'portrait'}
            };
            html2pdf().from(form).set(opt).save();
        })
}

// Displayed line count
function updateLineCount() {
    let table = document.getElementById("proof-table");
    let counter = 0;

    for (let i = 1; i < table.rows.length - 1; i++) {
        if (!table.rows[i].hidden) {
            counter++
        }
    }
    document.getElementById("line_counter").innerText = counter;
}


function update_comment_response_button() {
    let comment_forms = document.querySelectorAll(`[id$="comment"]`);
    let response_forms = document.querySelectorAll(`[id$="response"]`);

    comment_forms.forEach(function(form){
        const form_id = get_form_id(form)
        const form_add_comment_btn=document.getElementById(`id_${FORMSET_PREFIX}-${form_id}-comment-btn`)
        if (form.value.length > 0){
            set_comment_btn_active(form_add_comment_btn)
        } else {
            set_comment_btn_inactive(form_add_comment_btn)
            form.toggleAttribute("hidden")
        }
    })

    response_forms.forEach(function(form){
        const form_id = get_form_id(form)
        const form_add_response_btn=document.getElementById(`id_${FORMSET_PREFIX}-${form_id}-response-btn`)
        if (form.value.length > 0){
            set_response_btn_active(form_add_response_btn)
        } else {
            set_response_btn_inactive(form_add_response_btn)
            form.toggleAttribute("hidden")
        }
    })
}

function set_comment_btn_active(obj){
    if (obj !== null){
        obj.style.backgroundColor='#FDCA40'
        obj.children[0].style.fill='white'
    }
}

function set_comment_btn_inactive(obj){
    if (obj !== null){
        obj.style.backgroundColor=''
        obj.children[0].style.fill='orange'
    }
}

function set_response_btn_active(obj){
    if (obj !== null){
        obj.style.backgroundColor='#2e93a1'
        obj.children[0].style.fill='white'
    }
}

function set_response_btn_inactive(obj){
    if (obj !== null){
        obj.style.backgroundColor=''
        obj.children[0].style.fill='blue'
    }
}

function add_comment(obj){
    const comment_form = document.getElementById(`id_${FORMSET_PREFIX}-${get_form_id(obj)}-comment`)
    comment_form.toggleAttribute("hidden")
}

function add_response(obj){
    const comment_form = document.getElementById(`id_${FORMSET_PREFIX}-${get_form_id(obj)}-response`)
    comment_form.toggleAttribute("hidden")
}

/**
 * this function decides whether to show START_PROOF button or RESTART_PROOF button
 */
function set_start_restart_at_beginning() {
    //if it finds first rule field and that has some value.. then restart button is displayed.
    if (document.getElementById(`id_${FORMSET_PREFIX}-0-rule`) !== null && document.getElementById(`id_${FORMSET_PREFIX}-0-rule`).value !== '') {
        document.getElementById("btn_start_proof").hidden = true
        document.getElementById("btn_restart_proof").hidden = false
    } else {
        document.getElementById("btn_start_proof").hidden = false
        document.getElementById("btn_restart_proof").hidden = true
    }
}

function set_table_visibility() {
    //if it finds first rule field and that has some value.. then proof table is displayed.
    if (document.getElementById(`id_${FORMSET_PREFIX}-0-rule`) !== null && document.getElementById(`id_${FORMSET_PREFIX}-0-rule`).value !== '') {
        document.getElementById('proof-table').hidden = false
    }
}

/**
 * this function starts proof by inserting rows for premises and conclusions.
 */
function start_proof(element) {
    const premises = document.getElementById('id_premises').value;
    const premiseArray = premises.split(";").map(item => item.trim());
    const prooflineTableBody = document.getElementById(FORMSET_TBODY_ID);
    const proofTable = document.getElementById('proof-table');

    //Show proof table when after clicking Start Proof button
    proofTable.removeAttribute('hidden');

    // If there are zero premises:
    if ((premiseArray.length === 1) && (premiseArray[0] == "")) {
        let newRow = insert_form_helper(getTotalFormsCount())
        newRow.children[0].children[0].setAttribute("readonly", true)
        newRow.children[0].children[0].setAttribute("value", 1)
        prooflineTableBody.appendChild(newRow)

    } else {

        for (let i = 0; i < premiseArray.length; i++) {
            let newRow = insert_form_helper(getTotalFormsCount())
            let tds = newRow.children

            for (let x = 0; x < tds.length; x++) {
                let input = tds[x].children[0]
                // line_no
                if (x === 0) {
                    input.setAttribute("readonly", true)
                    input.setAttribute("value", i + 1)
                }
                // formula
                if (x === 1) {
                    input.setAttribute("value", `${premiseArray[i]}`)
                }
                // rule
                if (x === 2) {
                    input.setAttribute("value", 'Premise')
                }
            }
            prooflineTableBody.appendChild(newRow)
        }
    }

    update_form_count()
    hide_make_parent_button()
    element.hidden = true
    document.getElementById("btn_restart_proof").removeAttribute("hidden")
    reset_order_fields()
    updateLineCount()
}

/**
 * this function restarts proof by removing all rows and calling startProof method
 */
function restart_proof() {
    const initial_form_total_line = document.getElementById(FORMSET_INITIALLFORMS_ID).value;
    // if the initial form has value, then reload page
    if (initial_form_total_line > 0){
        location.reload();
    } else {
        delete_all_prooflines()
        start_proof(document.getElementById("btn_start_proof"))
        updateLineCount()
    }
}


function start_disproof(element) {
    document.getElementById('start_disproof_section').style.width = "250px";
    document.getElementById("main").style.marginRight = "250px";
    document.getElementById('btn_start_disproof').style.display = "none";
    document.getElementById('disproof_switches').innerHTML = "";

    // Get variables in premise and conclusion
    const variables = [];

    const premises = document.getElementById('id_premises').value;
    const premiseArray = premises.split(";").map(item => item.trim());

    for (let i = 0; i < premiseArray.length; i++) {
        for (let j = 0; j < premiseArray[i].length; j++) {
            if (is_letter(premiseArray[i][j])) {
                variables.push(premiseArray[i][j]);
            }
        }
    }

    const conclusion = document.getElementById('id_conclusion').value;
    for (let k = 0; k < conclusion.length; k++) {
        if (is_letter(conclusion[k])) {
            variables.push(conclusion[k]);
        }
    }

    let uniqueChars = [...new Set(variables)];

    // For each variable create a switch for it
    for (let v = 0; v < uniqueChars.length; v++) {
        document.getElementById('disproof_switches').innerHTML += `
        <div style="display: inline-block;">` + uniqueChars[v] + `</div>
        <label class="switch">
            <input type="checkbox">
            <span class="slider round"></span>
        </label>
        <br>
        `;
    }
}

function is_letter(str) {
    return str.length === 1 && str.match(/[a-z]/i);
}

function close_disproof() {
    document.getElementById('start_disproof_section').style.width = "0";
    document.getElementById("main").style.marginRight = "0";
    document.getElementById('btn_start_disproof').style.display = "block";
}


/**
 * Inserts form below current line
 */
function insert_form(obj) {
    //inserts new row with latest index at current object's next position
    insert_row_current_level(get_form_id(obj))
    hide_make_parent_button()
    reset_order_fields()
    update_row_indentations()
    updateLineCount()
}

/**
 * Concludes subproof by decreasing the depth of the current row
 */
function make_parent(obj) {
    const currentRow = document.getElementById(`${FORMSET_PREFIX}-${get_form_id(obj)}`)
    generate_parent_row(currentRow)
    hide_make_parent_button()
    reset_order_fields()
    update_row_indentations()
    updateLineCount()
}


/**
 * Inserts form below current line
 */
function create_subproof(obj) {
    const currentRow = document.getElementById(`${FORMSET_PREFIX}-${get_form_id(obj)}`)
    // Ifty Rahman - code to get previous row number, then 
    //compare to make sure we arent going in more than 1 level  beyond the immediate parent 
    const previousRow = getPreviousValidRow(currentRow)
    // Check if previousRow is null - this happens when we try to create sub proof for the first line
    // RECOMMENDATION: instead of having a check here, we can disable "create sub proof" button for the first line
    if (previousRow === null){
        alert("Can't create sub-proof for the first line")
        return
    }
    var maxIndent = check_if_max_indentation(currentRow,previousRow)
    if (maxIndent) {
        return
    }

    generate_new_subproof_row_number(currentRow)
    hide_make_parent_button()
    reset_order_fields()
    update_row_indentations()
    updateLineCount()
}

//function checks to see if the current row is 1 level in from the row above. Each subproof is always previous line + .1
function check_if_max_indentation(currentRow, previousRow) {
    let previousRowInfoObj = getObjectsRowInfo(previousRow) //get the information object from the row
    let currentRowInfoObj = getObjectsRowInfo(currentRow)
    let previousRowNumber = previousRowInfoObj.line_number_of_row //get the row number for a row from the row object
    let currentRowNumber = currentRowInfoObj.line_number_of_row
    let previousRowNumberOfPeriods = (previousRowNumber.match(/\./g) || []).length //count how many "." are in that row number
    let currentRowNumberOfPeriods = (currentRowNumber.match(/\./g) || []).length
    if (currentRowNumberOfPeriods == previousRowNumberOfPeriods + 1) { //if the number of periods in current row is 1 more than the previous, cant indent anymore
        alert("Can't indent any further")
        return true
    }
    return false
}

/**
 * Moves current row up
 */
function move_up(obj) {
    move_current_row_up(obj);
    update_row_indentations();
    hide_make_parent_button();
    reset_order_fields();
    update_comment_button();
}


/**
 * Move current row down
 */
function move_down(obj) {
    move_current_row_down(obj);
    update_row_indentations();
    hide_make_parent_button();
    reset_order_fields();
}

/**
 * delete current row
 */
function delete_form(obj) {
    delete_row(get_form_id(obj))
    reset_order_fields()
    hide_make_parent_button()
    update_row_indentations()
    updateLineCount()
}


// ---------------------------------------------------------------------------------------------------------------------
// Helper functions
// ---------------------------------------------------------------------------------------------------------------------

/**
 * generates new subproof row number
 */
function generate_new_subproof_row_number(currentRow) {

    // Get the row that the button was clicked
    const original_row_number_of_clicked_button = currentRow.children[0].children[0].value


    // Update row number of clicked button
    currentRow.children[0].children[0].value = `${original_row_number_of_clicked_button}.1`

    // If Rule is currently blank then add "Assumption" to the new subproof
    if (currentRow.children[2].children[0].value.length == 0) {
        currentRow.children[2].children[0].value = 'Assumption'
    }

    updated_rows = {};
    updated_rows[original_row_number_of_clicked_button] = currentRow.children[0].children[0].value;

    reset_order_fields()

    update_rule_line_references(updated_rows);


}


/**
 * generates new subproof row number
 */
function generate_parent_row(currentRow) {

    // Get the row that the button was clicked
    const original_row_number_of_clicked_button = currentRow.children[0].children[0].value

    const originalCurrentRowInfo = getObjectsRowInfo(currentRow);
    //get final value of prev row lineno and add 1 to it
    const originalCurrentRowLineNumberSegments = originalCurrentRowInfo.prefix_of_row;
    const originalCurrentRowLastNumberSegment = originalCurrentRowLineNumberSegments[originalCurrentRowLineNumberSegments.length - 1];

    originalCurrentRowLineNumberSegments[originalCurrentRowLineNumberSegments.length - 1] = originalCurrentRowInfo.final_value == 1 ? Number(originalCurrentRowLastNumberSegment) : Number(originalCurrentRowLastNumberSegment) + 1

    // originalCurrentRowLineNumberSegments[originalCurrentRowLineNumberSegments.length - 1] = Number(originalCurrentRowLastNumberSegment) + 1
    currentRow.children[0].children[0].value = originalCurrentRowLineNumberSegments.join('.')
    currentRow.children[0].children[0].setAttribute("readonly", true)

    updated_rows = {}
    if (originalCurrentRowInfo.final_value != 1) {
        updated_rows = renumber_rows(1, currentRow);
    }

    updated_rows[original_row_number_of_clicked_button] = currentRow.children[0].children[0].value;

    reset_order_fields()
    update_rule_line_references(updated_rows)
}


/**
 * inserts a row at current level when INSERT ROW button is clicked
 */
function insert_row_current_level(index) {
    const newRow = insert_new_form_at_index(index + 1);
    const prevRowInfo = getObjectsRowInfo(getPreviousValidRow(newRow));

    //get final value of prev row lineno and add 1 to it
    const prevRowLineNumberSegments = prevRowInfo.list_of_line_number;
    const prevRowLastNumberSegment = prevRowLineNumberSegments[prevRowLineNumberSegments.length - 1];
    //generating new row line numbers
    prevRowLineNumberSegments[prevRowLineNumberSegments.length - 1] = Number(prevRowLastNumberSegment) + 1
    newRow.children[0].children[0].value = prevRowLineNumberSegments.join('.')
    newRow.children[0].children[0].setAttribute("readonly", true)

    updated_rows = renumber_rows(1, newRow)
    reset_order_fields()

    update_rule_line_references(updated_rows)

}


/**
 * Moves the current row up
 */
function move_current_row_up(obj) {

    // Get the current row
    const currentRow = document.getElementById(`${FORMSET_PREFIX}-${get_form_id(obj)}`)
    const currentRowId = get_form_id(currentRow)

    // Get the previous row
    let previousRow = getPreviousValidRow(currentRow)

    // If the previous row is hidden then continue to search until you find a visible previous row or null
    while (true) {
        if (previousRow == null || !previousRow.hidden) {
            break;
        }
        previousRow = previousRow.previousElementSibling;
    }

    // If the previous row is not null then continue
    if (previousRow != null) {
        const previousRowId = get_form_id(previousRow)
        // Get previous row information
        let previousRowInfo = getObjectsRowInfo(previousRow);
        // Get current row information
        let currentRowInfo = getObjectsRowInfo(currentRow);

        // Get original previous row line number
        const originalPreviousRowLineNumber = previousRowInfo.line_number_of_row;
        // Get original previous row expression
        const originalPreviousRowExpression = document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-formula`).value
        // get original previous row rule
        const originalPreviousRowRule = document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-rule`).value
        //get original previous row comment
        const originalPreviousRowComment = document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-comment`).value
        //get original previous row response
        const originalPreviousRowResponse = document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-response`).value

        // Get original current row line number
        const originalCurrentRowLineNumber = currentRowInfo.line_number_of_row;
        // Get original current row expression
        // const originalCurrentRowExpression = currentRow.children[1].children[0].value;
        const originalCurrentRowExpression = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-formula`).value
        // get original current row rule
        //const originalCurrentRowRule = currentRow.children[2].children[0].value;
        const originalCurrentRowRule = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-rule`).value
        //get original current row comment
        const originalCurrentRowComment = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-comment`).value
        //get original current row response
        const originalCurrentRowResponse = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-response`).value

        // Insert row after previous row
        //let insertObj = previousRow.children[3].children[0]
        //let insertObj = document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-insert-btn`)
        insert_row_current_level(previousRowId);
        update_row_indentations()
        // Get the newly inserted row
        let newlyInsertedRow = previousRow.nextElementSibling;
        let newlyInsertedRowId = get_form_id(newlyInsertedRow)

        // If they are in line with each other then swap
        if (previousRowInfo.string_of_prefix == currentRowInfo.string_of_prefix) {
            // Change newly inserted row expression to the original previous row expression
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-formula`).value = originalPreviousRowExpression;
            // Change newly inserted row rule to the original previous row rule
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-rule`).value = originalPreviousRowRule;
            // Change newly inserted row comment to the original previous row comment
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-comment`).value = originalPreviousRowComment;
            // Change newly inserted row response to the original previous row response
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-response`).value = originalPreviousRowResponse;

            // Change previous row expression to the original current row expression
            document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-formula`).value = originalCurrentRowExpression;
            // Change previous row rule to the original current row rule
            document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-rule`).value = originalCurrentRowRule;
            // Change previous row comment to the original current row comment
            document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-comment`).value = originalCurrentRowComment
            // Change previous row response to the original current row response
             document.getElementById(`id_${FORMSET_PREFIX}-${previousRowId}-response`).value = originalCurrentRowResponse


            // Update the line references originally pointing to the current row to the previous row
            updated_rows[originalCurrentRowLineNumber] = originalPreviousRowLineNumber;
            // Update the line references originally pointing to the previous row to the newly added row
            updated_rows[originalPreviousRowLineNumber] = document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-line_no`).value
            update_rule_line_references(updated_rows);

        }
        // Otherwise move current in line
        else {
            // Change newly inserted row expression to the original current row expression
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-formula`).value = originalCurrentRowExpression
            // Change newly inserted row rule to the original current row rule
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-rule`).value = originalCurrentRowRule
            // Change newly inserted row comment to the original current row comment
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-comment`).value = originalCurrentRowComment;
            // Change newly inserted row response to the original current row response
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-response`).value = originalCurrentRowResponse;

            // Update the line references originally pointing to the current row to the newly added row
            updated_rows[originalCurrentRowLineNumber] = document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-line_no`).value
            update_rule_line_references(updated_rows)
        }
        // Delete the original current row
        delete_row(get_form_id(obj))
    }
}


/**
 * Moves the current row down
 */
function move_current_row_down(obj) {
    // Get the current row
    const currentRow = document.getElementById(`${FORMSET_PREFIX}-${get_form_id(obj)}`)
    const currentRowId = get_form_id(currentRow)


    // Get the next row
    let nextRow = getNextValidRow(currentRow)

    // If the next row is hidden move to the next element until you find one that's not hidden
    while (true) {
        if (nextRow == null || !nextRow.hidden) {
            break;
        }
        nextRow = nextRow.nextElementSibling
    }

    // If the next row is not null then move the row down
    if (nextRow != null) {
        let nextRowId = get_form_id(nextRow)
        // Get current row information
        let currentRowInfo = getObjectsRowInfo(currentRow);
        // Get next row information
        let nextRowInfo = getObjectsRowInfo(nextRow);

        // Get original current row line number
        const originalCurrentRowLineNumber = currentRowInfo.line_number_of_row;
        // Get original current row expression
        const originalCurrentRowExpression = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-formula`).value
        // get original current row rule
        const originalCurrentRowRule = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-rule`).value
        //get original current row comment
        const originalCurrentRowComment = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-comment`).value
        //get original current row response
        const originalCurrentRowResponse = document.getElementById(`id_${FORMSET_PREFIX}-${currentRowId}-response`).value


        // Get original next row line number
        const originalNextRowLineNumber = nextRowInfo.line_number_of_row;
        // Get original current row expression
        const originalNextRowExpression = document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-formula`).value
        // get original current row rule
        const originalNextRowRule = document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-rule`).value
        //get original current row comment
        const originalNextRowComment = document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-comment`).value
        //get original current row response
        const originalNextRowResponse = document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-response`).value

        // Insert row after next row
        insert_row_current_level(nextRowId);
        update_row_indentations()

        // Get information for inserted row
        let newlyInsertedRow = nextRow.nextElementSibling;
        const newlyInsertedRowId = get_form_id(newlyInsertedRow)

        // if the prefix of current and next match then it is a swap
        if (currentRowInfo.string_of_prefix == nextRowInfo.string_of_prefix) {
            // Change newly inserted row expression to the original previous row expression
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-formula`).value = originalCurrentRowExpression;
            // Change newly inserted row rule to the original previous row rule
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-rule`).value = originalCurrentRowRule;
            // Change newly inserted row comment to the original previous row comment
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-comment`).value = originalCurrentRowComment;
            // Change newly inserted row response to the original previous row response
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-response`).value = originalCurrentRowResponse;


            //Update the line references originally pointing to current row to newly added row
            updated_rows[originalCurrentRowLineNumber] = document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-line_no`).value
            update_rule_line_references(updated_rows)
        }
        // otherwise you're switching the level of current to match next
        else {
            // Change newly inserted row expression to the original next row expression
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-formula`).value = originalNextRowExpression
            // Change newly inserted row rule to the original next row rule
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-rule`).value = originalNextRowRule
            // Change newly inserted row comment to the original next row comment
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-comment`).value = originalNextRowComment;
            // Change newly inserted row response to the original next row response
            document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-response`).value = originalNextRowResponse;

            // Change next row expression to the original current row expression
            document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-formula`).value = originalCurrentRowExpression
            // Change next row rule to the original current row rule
            document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-rule`).value = originalCurrentRowRule
            // Change next row comment to the original current row comment
            document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-comment`).value = originalCurrentRowComment;
            // Change next row response to the original current row response
            document.getElementById(`id_${FORMSET_PREFIX}-${nextRowId}-response`).value = originalCurrentRowResponse;

            // Update the line references originally pointing to the current row to the next row
            updated_rows[originalCurrentRowLineNumber] = originalNextRowLineNumber
            // Update the line references originally potinting to the next row to the newly added row
            updated_rows[originalNextRowLineNumber] = document.getElementById(`id_${FORMSET_PREFIX}-${newlyInsertedRowId}-line_no`).value
            update_rule_line_references(updated_rows)

        }

        // Delete the original current row
        delete_row(get_form_id(obj))
    }

}


/**
 * deletes the row where obj is located
 */
function delete_row(deleted_row_index) {
    let deleted_row = document.getElementById(FORMSET_PREFIX + '-' + deleted_row_index);

    let deleted_row_value = deleted_row.children[0].children[0].value;

    while (true) {
        if (checkIfRowIsUnique(deleted_row) === true) {
            let deleted_row_info = getObjectsRowInfo(deleted_row)
            if (deleted_row_info.list_of_line_number.length > 1) {
                document.getElementById('id_' + FORMSET_PREFIX + '-' + deleted_row_index + '-line_no').value = deleted_row_info.string_of_prefix;
            } else {
                break;
            }
        } else {
            break;
        }
    }

    //mark checkbox true
    document.getElementById('id_' + FORMSET_PREFIX + '-' + deleted_row_index + '-DELETE').setAttribute("checked", "true")

    //hide row
    document.getElementById(FORMSET_PREFIX + '-' + deleted_row_index).hidden = true;
    updated_rows = renumber_rows(-1, deleted_row)
    deleted_row.children[0].children[0].value = '0'

    //if id fields is empty that means this deleted (hidden now) row is a new row.. not existing one.. so we can actually remove it.
    if (document.getElementById('id_' + FORMSET_PREFIX + '-' + deleted_row_index + '-id').value === '') {
        document.getElementById(FORMSET_PREFIX + '-' + deleted_row_index).remove()
        pullupProoflineFormIndex(deleted_row_index)
        update_form_count()
    }
    reset_order_fields()


    updated_rows[deleted_row_value] = "";
    update_rule_line_references(updated_rows)

}


// ---------------------------------------------------------------------------------------------------------------------
// Helper functions
// ---------------------------------------------------------------------------------------------------------------------

/**
 * Helper function to set multiple attributes at once
 */
function setAttributes(el, attrs) {
    for (const key in attrs) {
        el.setAttribute(key, attrs[key]);
    }
}


/**
 * Call this at end of any function that changes the amount of forms
 */
function update_form_count() {
    const fomrsetManagerTotalFormCounter = document.getElementById(FORMSET_TOTALFORMS_ID)
    let currentFormCount = document.getElementsByClassName(FORMSET_TR_CLASS).length
    fomrsetManagerTotalFormCounter.setAttribute('value', currentFormCount)
    // console.log(fomrsetManagerTotalFormCounter);
}


/**
 * returns total formset lines by counting number of TR elements that has class name = FORMST_TR_CLASS
 */
function getTotalFormsCount() {
    return document.getElementsByClassName(FORMSET_TR_CLASS).length
}

/**
 * returns total formset lines from formset manager
 */
function getTotalFormsCountFromFormsetManager() {
    return parseInt(document.getElementById(FORMSET_TOTALFORMS_ID).value)
}


/**
 * updates total formset count in formset manager
 */
function setTotalFormsCountInFormsetManager(value) {
    document.getElementById(FORMSET_TOTALFORMS_ID).setAttribute('value', value)
}

/**
 * extract formset index (numeric part) from object's id
 */
function get_form_id(obj) {
    return parseInt(obj.id.replace(/[^0-9]/g, ""))
}


/**
 * delete children from any DOM element
 */
function delete_all_prooflines() {
    if (document.getElementsByClassName(FORMSET_TR_CLASS).length >= 1) {
        let row = document.getElementById(`${FORMSET_PREFIX}-0`)

        while (row !== null) {
            let nextRow = row.nextElementSibling;
            delete_form(row);
            row = nextRow;
        }
    }
}


/**
 * this function reset ORDER (positional index) for each row. Django displays sorted lines based on this value
 */
function reset_order_fields() {
    const ORDER_fields = document.querySelectorAll('[id $= "-ORDER"]');
    let pos_index = 0;
    let index = null;
    for (let field of ORDER_fields) {
        if (field.id !== null && field.id.indexOf("__prefix__") < 0) {
            index = get_form_id(field)
            if (!document.getElementById(`${FORMSET_PREFIX}-${index}`).hidden) {
                field.value = pos_index++
                document.getElementById(`id_${FORMSET_PREFIX}-${index}-ORDER`).value = field.value
            } else {
                field.value = -1
            }

        }
    }
}


/**
 * this function sorts formset table based on ORDER (input no 12) field.
 */
function sort_table() {
    let switch_flag;
    let i, x, y;
    let switching = true;

    // Run loop until no switching is needed
    while (switching) {
        switching = false;
        const rows = document.getElementsByClassName(FORMSET_TR_CLASS);
        // Loop to go through all rows
        for (i = 1; i < (rows.length - 1); i++) {
            switch_flag = false;

            // Fetch 2 elements that need to be compared
            x = rows[i].getElementsByTagName("input")[5].value
            y = rows[i + 1].getElementsByTagName("input")[5].value

            // Check if 2 rows need to be switched
            if (parseInt(x) > parseInt(y)) {
                // If yes, mark Switch as needed and break loop
                switch_flag = true;
                break;
            }
        }
        if (switch_flag) {
            // Function to switch rows and mark switch as completed
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}


/**
 * Text replacement - replaces escape commands with symbols
 */
function replaceCharacter(e) {
    let txt = document.getElementById(e.id).value;
    txt = txt.replace("\\and", "∧");
    txt = txt.replace("\\or", "∨");
    txt = txt.replace("\\imp", "→");
    txt = txt.replace("\\not", "¬");
    txt = txt.replace("\\iff", "↔");
    txt = txt.replace("\\con", "⊥");
    txt = txt.replace("\\all", "∀");
    txt = txt.replace("\\exi", "∃");
    txt = txt.replace("\\in", "∈");
    document.getElementById(e.id).value = txt;

    //Change the comment button style accordingly depending on if comment form has data in it
    if (e.id.includes("comment")){
        const parentRowObj = e.parentNode.parentNode;
        const rowId = get_form_id(parentRowObj);
        const addCommentBtn = document.getElementById(`id_${FORMSET_PREFIX}-${rowId}-comment-btn`)
        if (txt.length > 0){
           set_comment_btn_active(addCommentBtn)

        } else {
           set_comment_btn_inactive(addCommentBtn)
        }   
    } else if (e.id.includes("response")) {
        const parentRowObj = e.parentNode.parentNode;
        const rowId = get_form_id(parentRowObj);
        const addResponsetBtn = document.getElementById(`id_${FORMSET_PREFIX}-${rowId}-response-btn`)
        if (txt.length > 0){
           set_response_btn_active(addResponsetBtn)

        } else {
           set_response_btn_inactive(addResponsetBtn)
        }   
    }

}


/**
 * this function clones empty form and get it ready for insertion at provided index
 */
function insert_form_helper(index) {
    const emptyFormElement = document.getElementById('empty-form').cloneNode(true)
    emptyFormElement.setAttribute("class", FORMSET_TR_CLASS)
    emptyFormElement.setAttribute("id", `${FORMSET_PREFIX}-${index}`)
    const regex = new RegExp('__prefix__', 'g')
    emptyFormElement.innerHTML = emptyFormElement.innerHTML.replace(regex, index)
    return emptyFormElement
}


/**
 * this function insert a new form at provided index
 */
function insert_new_form_at_index(index) {
    const getNextIndex = getTotalFormsCount(); //get the latest index
    const emptyFormElement = insert_form_helper(getNextIndex)
    const proof_tbody = document.getElementById(FORMSET_TBODY_ID)
    const proof_table_row = document.getElementById(FORMSET_PREFIX + '-' + (index - 1))
    if (proof_table_row !== null) {
        proof_table_row.after(emptyFormElement)
    } else {
        proof_tbody.append(emptyFormElement)
    }
    update_form_count()
    reset_order_fields()
    return emptyFormElement
}

/**
 * this function gets line no details of row at provided index
 */

function break_line_number(line_number_of_row) {
    // Get list of number of row
    const list_of_line_number = line_number_of_row.split('.');
    // Get the prefix of the row
    const prefix_of_row = list_of_line_number.slice(0, -1);
    // Get the string of the prefix
    const string_of_prefix = prefix_of_row.join('.');
    // Get the final value of row
    const final_value = list_of_line_number.slice(-1);

    return {
        // Get object of the row
        // "row_object": row_object,
        // Get line number of the row
        "line_number_of_row": line_number_of_row,
        // Get list of number of row
        "list_of_line_number": list_of_line_number,
        // Get the prefix of the row
        "prefix_of_row": prefix_of_row,
        // Get the string of the prefix
        "string_of_prefix": string_of_prefix,
        // Get the final value of row
        "final_value": final_value,
    }
}

function get_row(index) {
    const row_object = document.getElementById(FORMSET_PREFIX + '-' + (index));
    // Get line number of the row
    const line_number_of_row = row_object.children[0].children[0].value;

    return break_line_number(line_number_of_row)
}

/**
 * this function gets line no details of row at provided object's index
 */
function getObjectsRowInfo(row_object) {
    if (row_object === null) {
        return null
    }
    return get_row(get_form_id(row_object))
}


/**
 * this function finds next row in formset but ignores row(s) that is/are marked for deletion
 */
function getNextValidRow(currRow) {
    let nextRow = null;
    do {
        try {
            nextRow = currRow.nextElementSibling;
            if (nextRow.tagName === 'TR' && nextRow.classList.contains(FORMSET_TR_CLASS) && nextRow.children[7].children[1].getAttribute('checked') !== 'true') {
                break;
            } else {
                currRow = nextRow;
            }
        } catch (Error) {
            break;
        }
    } while (nextRow !== null && nextRow.tagName === 'TR')

    return nextRow;
}


/**
 * this function finds previous row in formset but ignores row(s) that is/are marked for deletion
 */
function getPreviousValidRow(currRow) {
    let prevRow = null;
    do {
        try {
            prevRow = currRow.previousElementSibling;
            if (prevRow.tagName === 'TR' && prevRow.classList.contains(FORMSET_TR_CLASS) && prevRow.children[7].children[1].getAttribute('checked') !== 'true') {
                break;
            } else {
                currRow = prevRow
            }
        } catch (Error) {
            break;
        }
    } while (prevRow !== null && prevRow.tagName === 'TR')

    return prevRow;
}


/**
 * this function reset line numbers in formset
 */

function checkIfRowIsUnique(currRow) {
    //getting the following valid row (ignoring rows that are already marked for deletion)
    let nextRow = getNextValidRow(currRow);
    //getting the previous valid row (ignoring deleted rows)
    let prevRow = getPreviousValidRow(currRow)

    //getting line no info of current row
    let currRowInfo = getObjectsRowInfo(currRow);
    //getting line no info of next row
    let nextRowInfo = getObjectsRowInfo(nextRow);
    //getting line no info of prev row
    let prevRowInfo = getObjectsRowInfo(prevRow)

    let lastItemCheck = false;

    if (currRowInfo.list_of_line_number.length === 1) {
        return true;
    } else {
        /*
        * if both prev n next rows exist
        *   if any of them has same length as curr row and matches prefix ---- then return false
        *
        * */

        if (nextRow !== null) {
            if (currRowInfo.list_of_line_number.length === nextRowInfo.list_of_line_number.length && currRowInfo.string_of_prefix === nextRowInfo.string_of_prefix) {
                return false;
            } else if (nextRowInfo.list_of_line_number.length > currRowInfo.list_of_line_number.length && nextRowInfo.string_of_prefix.startsWith(currRowInfo.string_of_prefix)) {
                return false;
            }
        }

        if (prevRow !== null) {
            if (currRowInfo.list_of_line_number.length === prevRowInfo.list_of_line_number.length && currRowInfo.string_of_prefix === prevRowInfo.string_of_prefix) {
                return false;
            }
            if (prevRowInfo.list_of_line_number.length > currRowInfo.list_of_line_number.length && prevRowInfo.string_of_prefix.startsWith(currRowInfo.string_of_prefix)) {
                return false;
            }
        }

        if (nextRow !== null && prevRow !== null) {
            //next row or prev row with same length doesn't have matching prefix
            if (prevRowInfo.list_of_line_number.length < currRowInfo.list_of_line_number.length && currRowInfo.list_of_line_number.length > nextRowInfo.list_of_line_number.length) {
                return true
            }
        }
        return true;
    }
}

function renumber_rows(direction, newlyChangedRow) {

    updated_rows = {}

    //getting currentRow that just got changed
    let currRow = newlyChangedRow;
    //getting the following valid row (ignoring rows that are already marked for deletion)
    let nextRow = getNextValidRow(currRow);
    //getting the previous valid row (ignoring deleted rows)
    let prevRow = getPreviousValidRow(currRow)

    //getting line no info of current row
    let currRowInfo = getObjectsRowInfo(newlyChangedRow);
    //getting line no info of next row
    let nextRowInfo = getObjectsRowInfo(nextRow);
    //getting line no info of prev row
    let prevRowInfo = getObjectsRowInfo(prevRow)

    let indexOfChangedElement = currRowInfo.list_of_line_number.length - 1
    let currRowStringOfPrefix = currRowInfo.string_of_prefix;

    //if there's no next row then no need to renumber the rows
    if (nextRow !== null) {
        while (nextRow !== null && nextRow.tagName === 'TR' && nextRow.classList.contains(FORMSET_TR_CLASS)) {
            //for insertion -- if current row is 3.1.1 and we do not have to increase line no for row that is on higher level than current row.. so 3.2 will not get updated.
            if (direction === 1 && currRowInfo.list_of_line_number.length > nextRowInfo.list_of_line_number.length) {
                break;
            }

            //if next row starts with current row's prefix then we will increase (for insert / direction 1) or decrease (for deletion / direction -1) next row's line number
            if (nextRowInfo.line_number_of_row.startsWith(currRowStringOfPrefix)) {

                let temporary_original_row = nextRow.children[0].children[0].value;

                nextRowInfo.list_of_line_number[indexOfChangedElement] = Number(nextRowInfo.list_of_line_number[indexOfChangedElement]) + direction
                const new_row_number = nextRowInfo.list_of_line_number.join('.');
                nextRow.children[0].children[0].value = new_row_number

                updated_rows[temporary_original_row] = new_row_number;

            }

            //setting up next for for next loop
            nextRow = getNextValidRow(nextRow)
            nextRowInfo = (nextRow !== null) ? getObjectsRowInfo(nextRow) : null;
        }
    }

    return updated_rows;
}


function update_rule_line_references(updated_rows) {

    if (document.getElementsByClassName(FORMSET_TR_CLASS).length >= 1) {
        let row = document.getElementById(`${FORMSET_PREFIX}-0`)

        while (row !== null) {
            if (!row.hidden) {
                let old_rule = row.children[2].children[0].value;
                let cleaned_rule = clean_rule(old_rule);
                let rule_text = cleaned_rule.split(/[ ,]+/);
                let new_rule_text = [rule_text[0]];

                for (let i = 0; i < rule_text.length; i++) {
                    if (rule_text[i] in updated_rows) {
                        // let original_value = rule_text[i]
                        let new_value = updated_rows[rule_text[i]]
                        if (new_value.length != 0) {
                            new_rule_text.push(new_value)
                        }
                    } else {
                        if (i > 0) {
                            new_rule_text.push(rule_text[i]);
                        }
                    }
                }
                for (let i = 0; i < new_rule_text.length; i++) {
                    if (i > 0 & i < new_rule_text.length - 1) {
                        new_rule_text[i] = `${new_rule_text[i]},`;
                    }
                }

                row.children[2].children[0].value = new_rule_text.join(" ");
            }
            row = row.nextElementSibling;
        }
    }
}

function clean_rule(old_rule) {
    rule_errors = ['∧ ', '∨ ', '¬ ', '→ ', '↔ ', '∀ ', '∃ '];
    new_rule = old_rule;
    let rule_prefix = old_rule.substring(0, 2);
    if (rule_errors.includes(rule_prefix)) {
        new_rule = old_rule[0] + old_rule.substring(2, old_rule.length)
    }
    return new_rule;
}


/** This function adds indentation to all of the sub proofs */
function update_row_indentations() {

    if (document.getElementsByClassName(FORMSET_TR_CLASS).length >= 1) {
        let row = document.getElementById(`${FORMSET_PREFIX}-0`)

        while (row !== null) {
            let row_number = row.children[0].children[0].value;
            let sub_proof_depth = row_number.match(/\./g) ? row_number.match(/\./g).length : 0;

            // Add a margin if it's a sub proof
            if (sub_proof_depth > 0) {
                let margin = 25 * sub_proof_depth
                row.children[0].children[0].style.marginLeft = `${margin}px`
            }
            // Remove any margin if it's a parent row
            else {
                row.children[0].children[0].style.marginLeft = `${0}px`
            }
            row = row.nextElementSibling;
        }
    }
}


/**
 * this function reset line numbers in formset
 */
function pullupProoflineFormIndex(to_index) {
    const last_form_element_id = getTotalFormsCountFromFormsetManager() - 1;
    for (let i = to_index + 1; i <= last_form_element_id; i++) {
        updateFormsetId(i, i - 1)
    }
}


/**
 * this function updates formset id. When a newly created row is deleted from DOM (in create and update scenario) we will need to pull up the indexes of succeeding rows.
 * in case of deleting rows that is currently in DB we are not deleting them from DOM so no need to update formset ids in that case.
 */
function updateFormsetId(old_id, new_id) {
    const targeted_element = document.getElementById(FORMSET_PREFIX + '-' + old_id)
    if (targeted_element !== null) {
        document.getElementById(FORMSET_PREFIX + '-' + old_id).setAttribute('id', `${FORMSET_PREFIX}-${new_id}`)
        const fields = ['line_no', 'formula', 'rule', 'insert-btn', 'make_parent-btn', 'create_subproof-btn', 'move_up-btn', 'move_down-btn', 'delete-btn', 'id', 'DELETE', 'ORDER', 'comment','response','comment-btn','response-btn']
        fields.forEach(function (field) {
            document.getElementById('id_' + FORMSET_PREFIX + '-' + old_id + '-' + field).setAttribute('name', `${FORMSET_PREFIX}-${new_id}-${field}`)
            document.getElementById('id_' + FORMSET_PREFIX + '-' + old_id + '-' + field).setAttribute('id', `id_${FORMSET_PREFIX}-${new_id}-${field}`)
        })
    }
}


function hide_make_parent_button() {

    let table = document.getElementById("proof-table");

    // Make all buttons visible
    let all_conclude_btn = document.getElementById(FORMSET_TBODY_ID).querySelectorAll('.make_parent')
    for (let i = 0; i < all_conclude_btn.length; i++) {
        all_conclude_btn.item(i).disabled = false
    }

    for (let i = 1; i < table.rows.length - 1; i++) {
        // console.log(table.rows[i])

        if (i == table.rows.length - 1) {
            break;
        }

        let curr_form_obj = table.rows[i];
        let next_form_obj = getNextValidRow(curr_form_obj)

        const current_row_info = getObjectsRowInfo(curr_form_obj)
        if (current_row_info.list_of_line_number.length === 1) {
            curr_form_obj.children[4].children[0].disabled = true
        }

        if (next_form_obj !== null) {
            const next_row_info = getObjectsRowInfo(next_form_obj)
            if (current_row_info.list_of_line_number.length > 1) {
                if (current_row_info.string_of_prefix === next_row_info.string_of_prefix) {
                    curr_form_obj.children[4].children[0].disabled = true

                }
            }
            curr_form_obj = next_form_obj
            next_form_obj = getNextValidRow(curr_form_obj)
        }
    }
}


// ---------------------------------------------------------------------------------------------------------------------
