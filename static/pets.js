
$(".click-pet").click(async function (evt) {

    if ($(evt.target).closest('.pets-like button').length || $(evt.target).closest('.pets-like-saved button').length) {
        return;
    }

    evt.preventDefault();

    const clickedElement = $(evt.target).closest('.click-pet')[0];
    let petId = clickedElement.getAttribute('data-pet-id');

    window.location.href = `/details?petId=${petId}`;

});

$(".pets-like").click(async function (evt) {
    evt.preventDefault();

    const clickedElement = $(evt.target).closest('.click-pet')[0];
    const petId = clickedElement.getAttribute('data-pet-id');
    const name = clickedElement.getAttribute('data-name');
    const organizationId = clickedElement.getAttribute('data-organization-id');

    console.log(petId)

    window.location.href = `/favorites?petId=${petId}&name=${name}&organizationId=${organizationId}`;
    // location.reload();

});


// // automatically click on 'apply filters button' on page load
// $(document).ready(function() {
//     $("#apply-location").click();
// });

// $('.pets-like').click(function() {
//     location.reload();
// });

$(".pets-like-saved").click(async function (evt) {
    evt.preventDefault();

    const clickedElement = $(evt.target).closest('.click-pet')[0];
    const petId = clickedElement.getAttribute('data-pet-id');
    // const name = clickedElement.getAttribute('data-name');
    // const organizationId = clickedElement.getAttribute('data-organization-id');

    console.log(petId)

    window.location.href = `/favorites2?petId=${petId}`;
    // location.reload();

});
