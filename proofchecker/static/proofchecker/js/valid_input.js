const premisesBox = document.getElementById('id_premises');
const conclusionBox = document.getElementById('id_conclusion');
const syntaxBox = document.getElementById('id_rules');

premisesBox.addEventListener("focusout", isValidPremiseInput);
conclusionBox.addEventListener("focusout", isValidConclusionInput);
syntaxBox.addEventListener("change", checkAllFields);

function isValidPremiseInput()
{
    let premiseInput = "";
    let syntaxChoice = syntaxBox.value;
    premiseInput = premisesBox.value;

    if(syntaxChoice.includes("tfl"))
    {
        if(premiseInput != "" && !isValidTFL(premiseInput).includes("This is a valid TFL statement"))
        {
            invalidPremiseInputMessage(isValidTFL(premiseInput));
        }
        else
        {
            clearPremiseErrorDiv();
        }   
    }
    else if(syntaxChoice.includes("fol"))
    {
        if(premiseInput != "" && !isValidFOL(premiseInput).includes("This is a valid FOL statement"))
        {
            invalidPremiseInputMessage(isValidFOL(premiseInput));
        }
        else
        {
            clearPremiseErrorDiv();
        }  
    }
    
}

function isValidConclusionInput()
{
    let conclusionInput = "";
    let syntaxChoice = syntaxBox.value;
    conclusionInput = conclusionBox.value;

    if(syntaxChoice.includes("tfl"))
    {
        if(conclusionInput != "" && !isValidTFL(conclusionInput).includes("This is a valid TFL statement"))
        {
            invalidConclusionInputMessage(isValidTFL(conclusionInput));
        }
        else
        {
            clearConclusionErrorDiv();
        }
    }
    else if(syntaxChoice.includes("fol"))
    {
        if(conclusionInput != "" && !isValidFOL(conclusionInput).includes("This is a valid FOL statement"))
        {
            invalidConclusionInputMessage(isValidFOL(conclusionInput));
        }
        else
        {
            clearConclusionErrorDiv();
        }
    }
    
}

function checkAllFields()
{
    isValidPremiseInput();
    isValidConclusionInput();
}


function invalidPremiseInputMessage(string){

    let errorString = "";
    errorString = string;
    let premiseHeader = "Premise Error: ";

    let errorDiv = document.getElementById('valid-premise-div');

    errorDiv.innerHTML = premiseHeader.bold() + errorString;
}


function invalidConclusionInputMessage(string){

    let errorString = "";
    errorString = string;
    let conclusionHeader = "Conclusion Error: ";

    let errorDiv = document.getElementById('valid-conclusion-div');

    errorDiv.innerHTML = conclusionHeader.bold() + errorString;
}

function clearPremiseErrorDiv()
{
    let errorDiv = document.getElementById('valid-premise-div');
    errorDiv.innerHTML = "";

}

function clearConclusionErrorDiv()
{
    let errorDiv = document.getElementById('valid-conclusion-div');
    errorDiv.innerHTML = "";
}