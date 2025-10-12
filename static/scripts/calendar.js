function getEventsForCurrentMonth(calendar) {
    const view = calendar.view;
    const events = calendar.getEvents();

    const thisMonthEvents = events.filter(event => {
        const date = event.start;
        return date >= view.currentStart && date < view.currentEnd;
    });

    return thisMonthEvents.map(event => ({
        title: event.title,
        start: event.start.toISOString(),
        studio: event.extendedProps.studio,
        class: event.extendedProps.class_id
    }));
}

document.addEventListener('DOMContentLoaded', function () {
    let calendarE1 = document.getElementById('calendar');
    let draggableE1 = document.getElementById('external-events');

    let calendar = new FullCalendar.Calendar(calendarE1, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            center: 'custom1',
        },
        eventDidMount: function (info) {
            let description = info.event.extendedProps.description;
            if (description) {
                info.el.setAttribute("data-bs-toggle", "tooltip");
                info.el.setAttribute("title", description);

                // Initialize Bootstrap tooltip
                new bootstrap.Tooltip(info.el);
            }
        },
        customButtons: {
            custom1: {
                text: 'Save Month',
                click: function () {
                    const events = getEventsForCurrentMonth(calendar);

                    fetch("/save_month", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(events)
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === "success") {
                                alert(data.message || "Month saved!");
                            } else {
                                alert("Error saving: " + (data.error || "Unknown error"));
                            }
                        })
                        .catch(err => {
                            console.error("Fetch failed:", err);
                            alert("Could not save month due to network or server error.");
                        });

                }
            }
        },
        dayMaxEventRows: true,
        views: {
            timeGrid: {
                dayMaxEventRows: 4
            }
        },
        editable: true,
        droppable: true,
        selectable: true,
        events: '/events',
        eventDataTransform: function (rawEventData) {
            return {
                ...rawEventData,
                extendedProps: {
                    studio: rawEventData.studio,
                    class: rawEventData.class_id
                }
            };
        },
        eventDragStop: function (info) {
            const trash = document.getElementById('trash-image');
            const trashRect = trash.getBoundingClientRect();
            const x = info.jsEvent.clientX;
            const y = info.jsEvent.clientY;

            if (
                x >= trashRect.left &&
                x <= trashRect.right &&
                y >= trashRect.top &&
                y <= trashRect.bottom
            ) {
                if (confirm('Delete this class?')) {
                    info.event.remove();
                }
            }
        }
    });

    calendar.render();

    new FullCalendar.Draggable(draggableE1, {
        itemSelector: '.fc-event',
        eventStartEditable: true,
        eventData: function (eventEl) {
            if (!eventEl) return null;

            const text = eventEl.innerText?.trim();
            const studio = eventEl.getAttribute('data-studio');
            if (!text) return null;

            return {
                title: text,
                studio: studio
            };
        }
    });

});
