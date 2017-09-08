/*globals jQuery, alert */

jQuery(function($) {

    "use strict";

    var inventory = null;

    function get_authenticator() {
        return $('input[name="_authenticator"]').val();
    }

    function fill_fields(selected) {
        var fields = $("#cfields");

        fields.empty();
        $.each(inventory[selected].fields, function(key, val) {
            fields.append(
                $("<option />", {
                    value: key,
                    html: val.title
                })
            );
        });
    }

    function fill_content_select() {
        var select = $("#content_types"),
            selected = select.val();

        select.empty();
        $.each(inventory, function(key, val) {
            var new_option;

            new_option = $("<option />", {
                value: key,
                html: val.title
            });
            select.append(
                new_option
            );
        });
        if (!selected) {
            selected = select.children().eq(0).val();
        }
        select.val(selected);
        fill_fields(selected);
    }

    function get_inventory() {
        $.getJSON("@@ambidexterityajax/resource_inventory?_authenticator=" + get_authenticator(), function(data) {
            var select = $("#content_types");

            inventory = data;
            fill_content_select();
            select.change(function () {
                fill_fields(select.val());
            });
        });
    }

    get_inventory();


});