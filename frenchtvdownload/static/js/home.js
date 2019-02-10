/*
 * JavaScript file for the application to demonstrate
 * using the API
 */

// Create the namespace instance
let ns = {};

// Create the model instance
ns.model = (function() {
    'use strict';

    let $event_pump = $('body');

    // Return the API
    return {
        'read_all_url': function() {
            let ajax_options = {
                type: 'GET',
                url: 'api/video',
                accepts: 'application/json',
                dataType: 'json'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_read_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },

        "addurl": function(url) {
            let ajax_options = {
                type: 'POST',
                url: `api/video?url=${url}`,
                accepts: 'application/json',
                contentType: 'plain/text'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_addurl_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },

        'remove': function(video_id) {
            let ajax_options = {
                type: 'DELETE',
                url: `api/video/${video_id}`,
                accepts: 'application/json',
                contentType: 'plain/text'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_delete_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },

        "download": function(video_id) {
            let ajax_options = {
                type: 'GET',
                url: `api/download/${video_id}`,
                accepts: 'application/json',
                contentType: 'plain/text'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_download_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },

        "cancel": function(video_id) {
            let ajax_options = {
                type: 'DELETE',
                url: `api/download/${video_id}`,
                accepts: 'application/json',
                contentType: 'plain/text'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_cancel_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },

        'status': function(video_id) {
            let ajax_options = {
                type: 'GET',
                url: `api/status/${video_id}`,
                accepts: 'application/json',
                contentType: 'plain/text'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_get_status_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },

        'read': function() {
            let ajax_options = {
                type: 'GET',
                url: 'api/people',
                accepts: 'application/json',
                dataType: 'json'
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_read_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
        create: function(person) {
            let ajax_options = {
                type: 'POST',
                url: 'api/people',
                accepts: 'application/json',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(person)
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_create_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
        update: function(person) {
            let ajax_options = {
                type: 'PUT',
                url: `api/people/${person.person_id}`,
                accepts: 'application/json',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(person)
            };
            $.ajax(ajax_options)
            .done(function(data) {
                $event_pump.trigger('model_update_success', [data]);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                $event_pump.trigger('model_error', [xhr, textStatus, errorThrown]);
            })
        },
    };
}());

// Create the view instance
ns.view = (function() {
    'use strict';

    let counter_map = new Map() ;

    let $person_id = $('#person_id'),
        $fname = $('#fname'),
        $lname = $('#lname');

    function Counter(video_id, delay) {
        var interval;

        function run() {
            ns.model.status(video_id) ; 
        }

        this.start = function () {
            interval = setInterval(run, delay);
        }

        this.stop = function () {
            clearInterval(interval) ;
        }
    }

    // return the API
    return {
        reset: function() {
            $person_id.val('');
            $lname.val('');
            $fname.val('').focus();
        },
        update_editor: function(person) {
            $person_id.val(person.person_id);
            $lname.val(person.lname);
            $fname.val(person.fname).focus();
        },
        build_table: function(url) {
            let rows = ''

            // clear the table
            $('.people table > tbody').empty();

            // did we get a people array?
            if (url) {

                // stop potential interval created during previous iteration 
                for (var counter of counter_map.entries()) {
                    counter[1].stop()
                }
                // then clear the map of all counter    
                counter_map.clear()
                
                for (let i=0, l=url.length; i < l; i++) {
                    rows += `<tr data-video-id="${url[i].video_id}">`
                    rows += `<td class="video_url">${url[i].url}</td>`

                    // set status color
                    let color ;
                    let tdbutton = `<td><button id="remove" onclick="ns.model.remove(${url[i].video_id})">Remove</button>` ;
                    switch (url[i].status) {
                        case "done":
                            color = "Aquamarine" ;
                            tdbutton += `</td>`
                            break
                        case "pending":
                            color = "CornflowerBlue" ;
                            tdbutton += `<button id="download" onclick="ns.model.download(${url[i].video_id})">Download</button></td>`
                            break
                        case "downloading":
                            // set an interval counter to get download progress
                            counter_map.set(url[i].video_id, new Counter(url[i].video_id, 2000))
                            color = "Plum" ;
                            tdbutton += `<button id="cancel" onclick="ns.model.cancel(${url[i].video_id})">Cancel</button></td>`
                            break ;
                    }

                    rows += `<td class="video_status" bgcolor="${color}">${url[i].status}</td>`

                    // convert date
                    var date = new Date(url[i].timestamp);
                    rows += `<td>${date.toLocaleDateString("fr-FR")} ${date.toLocaleTimeString("fr-FR")}</td>`;

                    rows += tdbutton
                    rows += `</tr>`;
                }

                $('table > tbody').append(rows);

                // start all the interval counter
                for (var counter of counter_map.entries()) {
                    counter[1].start()
                }
            }
        },
        // update downloading progress 
        update_status: function(data) {
            let $tbody = $('.people table > tbody') ;
            let $tr = $($tbody).find("tr[data-video-id='"+data.video_id+"']") ;

            switch (data.status) {
                // case "done":
                //     // download completed, remove counter and mark the entry as done
                //     var counter = counter_map.get(data.video_id)
                //     counter.stop()
                //     counter_map.delete(data.video_id)
                //     $tr.find(".video_status").text("done") ;
                //     $tr.find(".video_status").attr('bgcolor', 'green');
                // break ;

                // case "pending":
                //     // download interruted, remove counter and mark the entry as done
                //     var counter = counter_map.get(data.video_id)
                //     counter.stop()
                //     counter_map.delete(data.video_id)
                //     $tr.find(".video_status").text("pending") ;
                //     $tr.find(".video_status").attr('bgcolor', 'CornflowerBlue');
                // break ;
                case "no_update":
                    return true ;
                case "downloading":
                    $tr.find(".video_status").text(data.progress) ;
                    return true ;
                break ;    
            } 

            return false ;
        },
        error: function(error_msg) {
            $('.error')
                .text(error_msg)
                .css('visibility', 'visible');
            setTimeout(function() {
                $('.error').css('visibility', 'hidden');
            }, 3000)
        }
    };
}());

// Create the controller
ns.controller = (function(m, v) {
    'use strict';

    let model = m,
        view = v,
        $event_pump = $('body') ;
   
    // Get the data from the model after the controller is done initializing
    setTimeout(function() {
        model.read_all_url();
    }, 100)

    // Validate input
    function validate(fname, lname) {
        return fname !== "" && lname !== "";
    }

    // Create our event handlers
    $('#addurl').click(function(e) {
        let $url_to_download = $('#url') ;

        e.preventDefault();
        model.addurl($url_to_download.val()) ;
        e.preventDefault();
    });

    $('#download').click(function(e) {
        let $target = $(e.target) ;
        let $video_id = $target.parent().attr('data-video-id');
        let video_id = $video_id.val();

        e.preventDefault();
        model.download(video_id) ;
        e.preventDefault();
    });

    $('#remove').click(function(e) {
        let $target = $(e.target) ;
        let $video_id = $target.parent().attr('data-video-id');
        let video_id = $video_id.val();

        e.preventDefault();
        model.remove(video_id) ;
        e.preventDefault();
    });

    $('#cancel').click(function(e) {
        let $target = $(e.target) ;
        let $video_id = $target.parent().attr('data-video-id');
        let video_id = $video_id.val();

        e.preventDefault();
        model.cancel(video_id) ;
        e.preventDefault();
    });

    // Create our event handlers
    $('#create').click(function(e) {
        let fname = $fname.val(),
            lname = $lname.val();

        e.preventDefault();

        if (validate(fname, lname)) {
            model.create({
                'fname': fname,
                'lname': lname,
            })
        } else {
            alert('Problem with first or last name input');
        }
    });

    $('#update').click(function(e) {
        let person_id = $person_id.val(),
            fname = $fname.val(),
            lname = $lname.val();

        e.preventDefault();

        if (validate(fname, lname)) {
            model.update({
                person_id: person_id,
                fname: fname,
                lname: lname,
            })
        } else {
            alert('Problem with first or last name input');
        }
        e.preventDefault();
    });

    $('#reset').click(function() {
        view.reset();
    })

    // $('table > tbody').on('dblclick', 'tr', function(e) {
    //     let $target = $(e.target),
    //         person_id,
    //         fname,
    //         lname;

    //     person_id = $target
    //         .parent()
    //         .attr('data-person-id');

    //     fname = $target
    //         .parent()
    //         .find('td.fname')
    //         .text();

    //     lname = $target
    //         .parent()
    //         .find('td.lname')
    //         .text();

    //     view.update_editor({
    //         person_id: person_id,
    //         fname: fname,
    //         lname: lname,
    //     });
    // });

    // Handle the model events
    $event_pump.on('model_read_success', function(e, url) {
        view.build_table(url);
        view.reset();
    });

    $event_pump.on('model_addurl_success', function(e, data) {
        model.read_all_url();
    });

    $event_pump.on('model_download_success', function(e, data) {
        model.read_all_url();
    });

    $event_pump.on('model_cancel_success', function(e, data) {
    });

    $event_pump.on('model_delete_success', function(e, data) {
        model.read_all_url();
    });

    $event_pump.on('model_get_status_success', function(e, data) {
        let resp = view.update_status(data);

        if (resp == false)
        {
            model.read_all_url();
        }

    });

    $event_pump.on('model_create_success', function(e, data) {
        model.read();
    });

    $event_pump.on('model_update_success', function(e, data) {
        model.read();
    });

    $event_pump.on('model_error', function(e, xhr, textStatus, errorThrown) {
        let error_msg = textStatus + ': ' + errorThrown + ' - ' + xhr.responseJSON.detail;
        view.error(error_msg);
        console.log(error_msg);
    })

    // return {
    //     "delete": function(e) {
    //         let $target = $(e.target),
    //         $video_id = $target.parent().attr('data-video-id');
    
    //         let video_id = $video_id.val();
    
    //         e.preventDefault();
    //         model.delete(video_id) ;
    //         e.preventDefault();
    //     }
    // }
}(ns.model, ns.view));

