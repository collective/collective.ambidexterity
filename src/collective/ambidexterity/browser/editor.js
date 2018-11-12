/*globals window, jQuery, require, define, alert, setTimeout, ace */

// TODO: save and abandon need to be buttons in a single form.


if (require === undefined) {
    // plone 4
    require = function (reqs, torun) {
        'use strict';
        return torun(window.jQuery);
    };
}

if (window.jQuery && define) {
    define('jquery', [], function () {
        'use strict';
        return window.jQuery;
    });
}

require([
    'jquery',
    'ace'
], function($) {
    'use strict';

    var inventory = null,
        content_type_select = $("#content_types"),
        fields_select = $("#cfields"),
        data_form = $("#dataform"),
        abandon_button = $("#abandon_edits"),
        save_button = $("#save_edits"),
        field_scripts = ['default', 'validator', 'vocabulary'],
        watch_editor_changes = false,
        editor;


    function get_authenticator() {
        return $('#available_actions input[name="_authenticator"]').val();
    }


    function fill_fields(selected) {
        var fields = inventory[selected].fields,
            sorted_keys = Object.keys(fields),
            selected_field = fields_select.val();

        fields_select.empty();
        if (sorted_keys.length > 0) {
            sorted_keys.sort();
            $.each(sorted_keys, function(index, key) {
                fields_select.append(
                    $("<option />", {
                        value: key,
                        html: fields[key].title
                    })
                );
            });
            fields_select.show();
            fields_select.prev().show();
            $("#script_label").show();
        } else {
            fields_select.hide();
            fields_select.prev().hide();
            $("#script_label").hide();
        }
        if (!selected_field) {
            selected_field = fields_select.children().eq(0).val();
        }
        fields_select.val(selected_field);
        fields_select.change();
    }


    function fill_content_select() {
        var selected = content_type_select.val(),
            sorted_keys = Object.keys(inventory);

        content_type_select.empty();
        sorted_keys.sort();
        $.each(sorted_keys, function(index, key) {
            var new_option;

            new_option = $("<option />", {
                value: key,
                html: inventory[key].title
            });
            content_type_select.append(new_option);
        });
        if (!selected) {
            selected = content_type_select.children().eq(0).val();
        }
        content_type_select.val(selected);
        content_type_select.change();
        fill_fields(selected);
    }


    function get_inventory() {
        $.getJSON("@@ambidexterityajax/resource_inventory?_authenticator=" + get_authenticator(), function(data) {
            inventory = data;
            fill_content_select();
        });
    }


    function disable_actions() {
        $("#available_actions :input").attr('disabled', 'disabled');
    }


    function enable_actions() {
        $("#available_actions :input").removeAttr('disabled');
    }


    function editor_set_source(source) {
        var editor_session = editor.getSession();

        watch_editor_changes = false;
        editor_session.setValue(source);
        editor.gotoLine(1, 1);
        if (source.trim().startsWith('<')) {
            editor_session.setMode("ace/mode/html");
        } else {
            editor_session.setMode("ace/mode/python");
        }
        // Changing the source will have generated a change event,
        // so we need to fix our buttons.
        save_button.attr('disabled', 'disabled');
        abandon_button.attr('disabled', 'disabled');
        enable_actions();
    }


    function clear_editor() {
        watch_editor_changes = false;
        editor.getSession().setValue('');
        data_form.children("#edit-label").text('');
    }


    function init_events() {
        content_type_select.change(function () {
            var content_type = content_type_select.val();

            fill_fields(content_type);
            if (inventory[content_type].has_view) {
                $('#add_view').hide();
                $('#edit_view').show();
                $('#remove_view').show();
            } else {
                $('#add_view').show();
                $('#edit_view').hide();
                $('#remove_view').hide();
            }
            if (inventory[content_type].has_custom_schema) {
                $('#add_custom_schema').hide();
                $('#edit_custom_schema').show();
                $('#remove_custom_schema').show();
            }else{
                $('#add_custom_schema').show();
                $('#edit_custom_schema').hide();
                $('#remove_custom_schema').hide();
            }
            $('#export_form input[name="ctype"]').val(content_type);
            if (inventory[content_type].has_view || Object.keys(inventory[content_type].fields).length > 0) {
                $('#export_form input[type="submit"]').removeAttr('disabled');
            } else {
                $('#export_form input[type="submit"]').attr('disabled', 'disabled');
            }
        });

        fields_select.change(function () {
            var content_type = content_type_select.val(),
                field_name = fields_select.val(),
                field_info = inventory[content_type].fields[field_name];

            if (field_name) {
                $.each(field_scripts, function(index, value) {
                    if (field_info['has_' + value]) {
                        $('#add_' + value).hide();
                        $('#edit_' + value).show();
                        $('#remove_' + value).show();
                    } else {
                        $('#add_' + value).show();
                        $('#edit_' + value).hide();
                        $('#remove_' + value).hide();
                    }
                    if (!field_info.allow_vocabulary) {
                        $('#add_vocabulary').hide();
                    }
                });
            } else {
                $.each(field_scripts, function(index, value) {
                    $('#add_' + value).hide();
                    $('#edit_' + value).hide();
                    $('#remove_' + value).hide();
                });
            }
            clear_editor();
        });

        $("form#available_actions button").click(function (e) {
            var button_id = $(this).attr('id'),
                content_type = content_type_select.val(),
                field_name = fields_select.val(),
                data_in;

            data_in = {
                "button_id": button_id,
                "content_type": content_type,
                "field_name": field_name
            };

            $.post("@@ambidexterityajax/button_action?_authenticator=" + get_authenticator(), data_in, function(data) {
                clear_editor();
                if (data.action === 'edit') {
                    editor_set_source(data.source);
                    data_form.children("#edit-label").text(
                        'Editing ' + button_id.replace('edit_', '') + ' for ' + content_type + '/' + field_name
                    );
                    data_form.children("input[name='content_type']").val(content_type);
                    data_form.children("input[name='field_name']").val(field_name);
                    data_form.children("input[name='script']").val(button_id);
                    watch_editor_changes = true;
                } else {
                    // an add or remove
                    get_inventory();
                    if (button_id.startsWith('add_')) {
                        // push the edit button
                        setTimeout(function () {
                            $('#edit_' + button_id.replace('add_', '')).eq(0).click();
                        }, 100);
                    }
                }
            }, 'json');
        });


        save_button.click(function (e) {
            var data_in = {
                content_type: data_form.children("input[name='content_type']").val(),
                field_name: data_form.children("input[name='field_name']").val(),
                script: data_form.children("input[name='script']").val(),
                data: editor.getValue(),
                save_action: "_authenticator=" + get_authenticator()
            };

            e.preventDefault();
            $.post("@@ambidexterityajax/save_action", data_in, function(data) {
                if (data.result === 'success') {
                    enable_actions();
                    save_button.attr('disabled', 'disabled');
                    abandon_button.attr('disabled', 'disabled');
                } else {
                    alert("Save failed.");
                }
            }, 'json');
        });


        abandon_button.click(function (e) {
            e.preventDefault();
            if (window.confirm("Do you wish to abandon changes?")) {
                clear_editor();
                enable_actions();
            }
        });


        data_form.submit(function (e) {
            e.preventDefault();
            alert("onSubmit for data_form");
        });
    } // init_events


    function editor_init() {
        if (!editor) {
            var editor_session;

            // set initial height
            $("#source_editor").height($(window).height() - 400);

            if (!window.ace) {
                // XXX hack...
                // wait, try loading later
                setTimeout(function () {
                    editor_init();
                }, 200);
                return;
            }
            editor = ace.edit("source_editor");
            editor.$blockScrolling = Infinity;
            // editor.setTheme("ace/theme/monokai");
            editor.setHighlightActiveLine(false);
            editor_session = editor.getSession();
            // editor_session.setMode("ace/mode/python");
            editor_session.setTabSize(4);
            editor_session.setUseSoftTabs(true);
            editor_session.setUseWrapMode(true);

            // Make save keystroke trigger save-form submit
            editor.commands.addCommand({
                name: "save",
                bindKey: {win: "Ctrl-S", mac: "Command-S"},
                exec: function() {
                    save_button.click();
                }
            });

            // enable save submit button on change
            editor_session.on('change', function(e) {
                if (watch_editor_changes) {
                    save_button.removeAttr('disabled');
                    abandon_button.removeAttr('disabled');
                    disable_actions();
                }
            });
        }
    } // editor_init


    get_inventory();
    editor_init();
    init_events();
});
