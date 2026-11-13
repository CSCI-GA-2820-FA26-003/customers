$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    function update_form_data(customer) {
        $("#customer_first_name").val(customer.first_name);
        $("#customer_last_name").val(customer.last_name);
        $("#customer_street").val(customer.street);
        $("#customer_city").val(customer.city);
        $("#customer_state").val(customer.state);
        $("#customer_postal_code").val(customer.postal_code);
        $("#customer_id").val(customer.id);
        $("#customer_membership_level").val(customer.membership_level);
    }

    function clear_form_data() {
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_street").val("");
        $("#customer_city").val("");
        $("#customer_state").val("");
        $("#customer_postal_code").val("");
        $("#customer_id").val("");
        $("#customer_membership_level").val("");
    }

    $("#customer_retrieve-btn").click(function () {
        const id = $("#customer_id").val().trim();
        if (!/^[1-9]\d*$/.test(id)) {
            alert("Enter a valid Customer ID");
            return;
        }

        $.getJSON(`/customers/${id}`)
            .done(function (customer) {
                update_form_data(customer);
                alert("Success");
            })
            .fail(function (response) {
                const message = response.responseJSON?.message || "Unable to retrieve customer";
                alert(message);
            });
    });

    function show_error(response) {
        const message = response.responseJSON?.message || response.responseText || "Server error!";
        alert(`Unable to create customer: ${message}`);
    }

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#customer_create-form").submit(function (event) {
        event.preventDefault();

        const data = {
            first_name: $("#customer_first_name").val(),
            last_name: $("#customer_last_name").val(),
            street: $("#customer_street").val(),
            city: $("#customer_city").val(),
            state: $("#customer_state").val(),
            postal_code: $("#customer_postal_code").val()
        };

        $.ajax({
            type: "POST",
            url: "/customers",
            contentType: "application/json",
            data: JSON.stringify(data)
        })
            .done(function (response) {
                update_form_data(response);
                alert(`Customer ${response.first_name} ${response.last_name} was successfully created!`);
            })
            .fail(show_error);
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#customer_clear-btn").click(function () {
        clear_form_data();
    });

    // ****************************************
    // State options
    // ****************************************

    const states = [
        ["AL", "Alabama"], ["AK", "Alaska"], ["AS", "American Samoa"],
        ["AZ", "Arizona"], ["AR", "Arkansas"], ["CA", "California"],
        ["CO", "Colorado"], ["CT", "Connecticut"], ["DE", "Delaware"],
        ["DC", "District of Columbia"], ["FM", "Federated States of Micronesia"],
        ["FL", "Florida"], ["GA", "Georgia"], ["GU", "Guam"], ["HI", "Hawaii"],
        ["ID", "Idaho"], ["IL", "Illinois"], ["IN", "Indiana"], ["IA", "Iowa"],
        ["KS", "Kansas"], ["KY", "Kentucky"], ["LA", "Louisiana"],
        ["ME", "Maine"], ["MH", "Marshall Islands"], ["MD", "Maryland"],
        ["MA", "Massachusetts"], ["MI", "Michigan"], ["MN", "Minnesota"],
        ["MS", "Mississippi"], ["MO", "Missouri"], ["MT", "Montana"],
        ["NE", "Nebraska"], ["NV", "Nevada"], ["NH", "New Hampshire"],
        ["NJ", "New Jersey"], ["NM", "New Mexico"], ["NY", "New York"],
        ["NC", "North Carolina"], ["ND", "North Dakota"],
        ["MP", "Northern Mariana Islands"], ["OH", "Ohio"], ["OK", "Oklahoma"],
        ["OR", "Oregon"], ["PW", "Palau"], ["PA", "Pennsylvania"],
        ["PR", "Puerto Rico"], ["RI", "Rhode Island"], ["SC", "South Carolina"],
        ["SD", "South Dakota"], ["TN", "Tennessee"], ["TX", "Texas"],
        ["UT", "Utah"], ["VT", "Vermont"], ["VI", "U.S. Virgin Islands"],
        ["VA", "Virginia"], ["WA", "Washington"], ["WV", "West Virginia"],
        ["WI", "Wisconsin"], ["WY", "Wyoming"]
    ];

    const stateSelect = $("#customer_state");
    stateSelect.append(new Option("", ""));
    states.forEach(function (state) {
        stateSelect.append(new Option(state[0], state[0]));
    });
});
