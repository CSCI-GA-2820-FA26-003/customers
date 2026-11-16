$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    function update_form_data(customer) {
        $("#customer_first_name").val(customer.first_name);
        $("#customer_last_name").val(customer.last_name);
        $("#customer_email").val(customer.email);
        $("#customer_street").val(customer.street);
        $("#customer_city").val(customer.city);
        $("#customer_state").val(customer.state);
        $("#customer_postal_code").val(customer.postal_code);
        $("#customer_membership_level").val(customer.membership_level);
    }

    function clear_form_data() {
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_email").val("");
        $("#customer_street").val("");
        $("#customer_city").val("");
        $("#customer_state").val("");
        $("#customer_postal_code").val("");
        $("#customer_membership_level").val("");
    }

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
            email: $("#customer_email").val(),
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
    // list all Customers
    // ****************************************

    $("#customer_query-form").submit(function (event) {
        event.preventDefault();

        const button = $("#customer_search-btn");
        button.prop("disabled", true);

        const filters = {};
        [
            "first_name", "last_name", "city", 
            "state", "postal_code", "membership_level"
        ].forEach(function(field){
            const value = $("#customer_query_" + field).val();
            if (value && value.trim()) {
                filters[field] = value.trim();
            }
        });

        $.ajax({
            type: "GET",
            url: "/customers",
            data: filters
        })
        .done(function(response){
            const tbody = $("#customer_search_results tbody");
            tbody.empty();
            set_manage_tab_enabled(response.length > 0);
            if (response.length === 0) {
                alert("Customer does not exist with the given search criteria.");
                return;
            }
            response.forEach(function (customer){
                const row = $("<tr></tr>");
                [
                    customer.id,
                    customer.first_name,
                    customer.last_name,
                    customer.street,
                    customer.city,
                    customer.state,
                    customer.postal_code,
                    customer.membership_level
                ].forEach(function(value){
                    row.append($("<td></td>").text(value));
                });
                row.data("customer", customer);
                tbody.append(row);
            });
        })
        .fail(function(response){
            const message = response.responseJSON?.message || "Server error!";
            alert(`Unable to list customers: ${message}`);
        })
        .always(function () {
            button.prop("disabled", false);
        });
    });

    // ****************************************
    // Open a search result in Manage Customer
    // ****************************************

    function update_manage_form(customer) {
        [
            "id", "first_name", "last_name", "email", "street",
            "city", "state", "postal_code", "membership_level"
        ].forEach(function (field) {
            $("#customer_manage_" + field).val(customer[field]);
        });
        $("#customer_delete_id").val(customer.id);
        update_upgrade_options(customer.membership_level);
    }

    // ****************************************
    // Upgrade a Customer's membership
    // ****************************************

    const MEMBERSHIP_LEVELS = ["bronze", "silver", "gold"];

    // Only offer levels above the current one; the API rejects downgrades
    function update_upgrade_options(current_level) {
        const select = $("#customer_upgrade_level");
        select.empty();
        const higher = MEMBERSHIP_LEVELS.slice(MEMBERSHIP_LEVELS.indexOf(current_level) + 1);
        if (higher.length === 0) {
            select.append(new Option("Already at highest level", ""));
        } else {
            higher.forEach(function (level) {
                const label = level.charAt(0).toUpperCase() + level.slice(1);
                select.append(new Option(label, level));
            });
        }
        select.prop("disabled", higher.length === 0);
        $("#customer_upgrade-btn").prop("disabled", higher.length === 0);
    }

    $("#customer_upgrade-form").submit(function (event) {
        event.preventDefault();

        const id = $("#customer_manage_id").val();
        const target_level = $("#customer_upgrade_level").val();
        const button = $("#customer_upgrade-btn");
        if (!id || !target_level) {
            return;
        }
        button.prop("disabled", true);

        $.ajax({
            type: "PUT",
            url: `/customers/${id}/upgrade`,
            contentType: "application/json",
            data: JSON.stringify({ target_level: target_level })
        })
            .done(function (response) {
                update_manage_form(response);
                // Keep the search results in sync with the new level
                $("#customer_search_results tbody tr").each(function () {
                    const row = $(this);
                    if (row.data("customer")?.id === response.id) {
                        row.data("customer", response);
                        row.children().last().text(response.membership_level);
                    }
                });
                alert(`Customer ${response.first_name} ${response.last_name} was successfully upgraded!`);
            })
            .fail(function (response) {
                const message = response.responseJSON?.message || response.responseText || "Server error!";
                alert(`Unable to upgrade customer: ${message}`);
                button.prop("disabled", false);
            });
    });

    // The Manage tab is only usable once a search has returned results
    function set_manage_tab_enabled(enabled) {
        const tab = $("#manage-tab");
        tab.parent().toggleClass("disabled", !enabled);
        tab.attr("aria-disabled", String(!enabled));
        tab.attr("title", enabled ? "" : "Search for customers first");
    }

    // Runs before Bootstrap's delegated tab handler on document
    $("#manage-tab").on("click", function (event) {
        if ($(this).parent().hasClass("disabled")) {
            event.preventDefault();
            event.stopPropagation();
        }
    });

    $("#customer_search_results tbody").on("click", "tr", function () {
        const customer = $(this).data("customer");
        if (!customer) {
            return;
        }
        update_manage_form(customer);
        $("#manage-tab").tab("show");
    });

    $("#customer_read-form").submit(function (event) {
        event.preventDefault();

        const id = $("#customer_id").val().trim();
        const result = $("#customer_result");
        const button = $("#customer_retrieve-btn");

        result.prop("hidden", true);
        button.prop("disabled", true);

        $.ajax({
            type: "GET",
            url: `/customers/${id}`,
            dataType: "json"
        })
            .done(function (response) {
                result.find("[data-field]").each(function () {
                    $(this).text(response[this.dataset.field]);
                });
                result.prop("hidden", false);
            })
            .fail(function (response) {
                const message = response.responseJSON?.message || response.responseText || "Server error!";
                alert(`Unable to retrieve customer: ${message}`);
            })
            .always(function () {
                button.prop("disabled", false);
            });
    });

    // ****************************************
    // Delete a Customer
    // ****************************************

    $("#customer_delete-form").submit(function (event) {
        event.preventDefault();

        const id = $("#customer_delete_id").val().trim();
        const button = $("#customer_delete-btn");
        button.prop("disabled", true);

        $.ajax({
            type: "DELETE",
            url: `/customers/${id}`
        })
            .done(function () {
                $("#customer_result").prop("hidden", true);
                alert("Success");
            })
            .fail(function (response) {
                const message = response.responseJSON?.message || response.responseText || "Server error!";
                alert(`Unable to delete customer: ${message}`);
            })
            .always(function () {
                button.prop("disabled", false);
            });
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

    ["#customer_state", "#customer_query_state", "#customer_manage_state"].forEach(function (selector) {
        const stateSelect = $(selector);
        stateSelect.append(new Option("", ""));
        states.forEach(function (state) {
            stateSelect.append(new Option(state[0], state[0]));
        });
    });

});
