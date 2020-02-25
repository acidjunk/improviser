import structlog
from apis.v1.exercises import transpose_chord_info

logger = structlog.get_logger(__name__)


def fix_exercise_chords(exercise):
    for item in exercise.riff_exercise_items:
        if item.riff.number_of_bars != item.number_of_bars:
            logger.info(
                "Correcting number_of_bars for exercise_item", item=item.order_number,
                number_of_bars=item.riff.number_of_bars
            )
            item.number_of_bars = item.riff.number_of_bars

        # Disable check, and just re-generate them all
        new_chord_info = None
        # Check chord syntax
        # *Cm7 and Cm7 will be converted to c1:m7
        # new_chord_info = None
        # if item_chord_info:
        #     if item_chord_info.startswith("*"):
        #         item_chord_info = item_chord_info[1:]
        #     if item_chord_info[0].isupper():
        #         try:
        #             new_chord_info = transpose_chord_info(
        #                 item_chord_info, "c", number_of_bars=item.riff.number_of_bars,
        #             )
        #             logger.info(
        #                 "Correcting chord for exercise_item from item",
        #                 current_chord_info=item_chord_info,
        #                 new_chord_info=new_chord_info,
        #             )
        #         except ValueError:
        #             logger.warning("No repair possible based on current item chord_info",
        #                            current_chord_info=item_chord_info)
        #             pass

        # item_chord_info = item.chord_info
        # Do them all
        item_chord_info = None

        if new_chord_info is None and item_chord_info is None:
            if item.riff.chord_info:
                new_chord_info = transpose_chord_info(item.riff.chord_info, item.pitch, number_of_bars=item.riff.number_of_bars)
                logger.info(
                    "Correcting chord for exercise_item from riff CHORD_INFO",
                    current_chord_info=item.riff.chord_info,
                    new_chord_info=new_chord_info,
                )
                # Correct it
                item.chord_info = new_chord_info
            elif item.riff.chord:
                new_chord_info = transpose_chord_info(item.riff.chord, item.pitch, number_of_bars=item.riff.number_of_bars)
                logger.info(
                    "Correcting chord for exercise_item from riff CHORD",
                    current_chord_info=item.riff.chord,
                    new_chord_info=new_chord_info,
                )
                # Correct it
                item.chord_info = new_chord_info
            else:
                logger.error("No chord info found in riff: this shouldn't happen", riff_id=item.riff_id)
