document.addEventListener(
    "DOMContentLoaded",
    function () {

        const focusableSelector = [
            "input:not([disabled]):not([readonly])",
            "select:not([disabled])",
            "textarea:not([disabled])",
            "button:not([disabled])",
            "a.menu-button"
        ].join(",");


        function getFocusableElements() {

            return Array.from(
                document.querySelectorAll(
                    focusableSelector
                )
            ).filter(function (element) {

                return (
                    element.offsetParent !== null
                );

            });

        }


        function moveFocus(direction) {

            const elements =
                getFocusableElements();


            if (elements.length === 0) {

                return;

            }


            const current =
                document.activeElement;


            const currentIndex =
                elements.indexOf(current);


            if (currentIndex === -1) {

                elements[0].focus();

                return;

            }


            let nextIndex =
                currentIndex + direction;


            if (
                nextIndex < 0
            ) {

                nextIndex =
                    elements.length - 1;

            }


            if (
                nextIndex >= elements.length
            ) {

                nextIndex = 0;

            }


            elements[nextIndex].focus();

        }


        document.addEventListener(
            "keydown",
            function (event) {

                const current =
                    document.activeElement;


                if (!current) {

                    return;

                }


                /*
                 * Do not interfere with
                 * normal text editing.
                 */

                if (
                    current.tagName ===
                    "TEXTAREA"
                ) {

                    return;

                }


                /*
                 * LEFT / RIGHT
                 *
                 * Keep normal browser behavior
                 * inside text inputs.
                 */

                if (
                    event.key === "ArrowLeft" ||
                    event.key === "ArrowRight"
                ) {

                    return;

                }


                /*
                 * UP
                 */

                if (
                    event.key === "ArrowUp"
                ) {

                    event.preventDefault();

                    moveFocus(-1);

                    return;

                }


                /*
                 * DOWN
                 */

                if (
                    event.key === "ArrowDown"
                ) {

                    event.preventDefault();

                    moveFocus(1);

                    return;

                }


                /*
                 * ENTER
                 *
                 * Move to the next control.
                 *
                 * If the current element is a
                 * button or menu link, allow its
                 * normal activation.
                 */

                if (
                    event.key === "Enter"
                ) {

                    const tag =
                        current.tagName;


                    if (
                        tag === "BUTTON" ||
                        tag === "A"
                    ) {

                        return;

                    }


                    event.preventDefault();

                    moveFocus(1);

                }

            }
        );

    }
);