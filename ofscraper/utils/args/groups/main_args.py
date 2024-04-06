import itertools
import re

import cloup as click

# import click
from humanfriendly import parse_size

import ofscraper.utils.args.groups.common_args as common
import ofscraper.utils.args.helpers as helpers


@click.group(
    help="Program Args",
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=True,
)
@click.option_group(
    "posts",
    click.option(
        "-q",
        "--quality",
        type=click.Choice(["240", "720", "source"], case_sensitive=False),
    ),
    click.option(
        "-o",
        "--posts",
        "--post",
        help="""
        Select areas for batch actions (comma or space separated).
        Options: HighLights, Archived, Messages, Timeline, Pinned, Stories, Purchased, Profile, Labels, All
        """,
        default=[],
        required=False,
        type=helpers.posttype_helper,
        callback=lambda ctx, param, value: (
            list(set(itertools.chain.from_iterable(value))) if value else []
        ),
        multiple=True,
    ),
    click.option(
        "-da",
        "--download-area",
        "download_area",
        help="""
        Perform download in specified areas (comma or space separated).
        Options: HighLights, Archived, Messages, Timeline, Pinned, Stories, Purchased, Profile, Labels, All
        Has preference over --posts
        """,
        default=[],
        required=False,
        type=helpers.download_helper,
        callback=lambda ctx, param, value: (
            list(set(itertools.chain.from_iterable(value))) if value else []
        ),
        multiple=True,
    ),
    click.option(
        "-la",
        "--like-area",
        help="""
        Perform like/unlike in selected areas (comma or space separated).
        Options: Archived, Timeline, Pinned, Labels, All
        Has preference over --posts
        """,
        default=[],
        required=False,
        type=helpers.like_helper,
        callback=lambda ctx, param, value: (
            list(set(itertools.chain.from_iterable(value))) if value else []
        ),
        multiple=True,
    ),
    click.option(
        "-ft",
        "--filter",
        help="Filter posts by regex (case-sensitive if uppercase characters included)",
        default=".*",
        required=False,
        type=str,
    ),
    click.option(
        "-nf",
        "--neg-filter",
        help="Filter posts to exclude those matching regex (case-sensitive if uppercase characters included)",
        default=None,
        required=False,
        type=str,
    ),
    click.option(
        "-sp",
        "--scrape-paid",
        help="Scrape entire paid page (can take a very long time)",
        default=None,
        is_flag=True,
    ),
    click.option(
        "-xc",
        "--max-count",
        help="Maximum number of posts to download (oldest non-duped first)",
        default=0,
        type=int,
    ),
    click.option(
        "-it",
        "--item-sort",
        help="Change item/post order before action (default: date asc or random)",
        default=None,
        required=False,
        type=click.Choice(
            [
                "random",
                "text-asc",
                "text-desc",
                "date-asc",
                "date-desc",
                "filename-asc",
                "filename-desc",
            ]
        ),
    ),
    click.constraints.mutually_exclusive(
        click.option(
            "-e",
            "--force-all",
            help="Download all files regardless of database presence",
            default=False,
            is_flag=True,
        ),
        click.option(
            "-eq",
            "--force-model-unique",
            help="Only download files not present for the current model in the database",
            default=False,
            is_flag=True,
        ),
    ),
    click.constraints.mutually_exclusive(
        click.option(
            "-to",
            "--protected-only",
            help="Only download content that requires decryption",
            default=False,
            is_flag=True,
        ),
        click.option(
            "-no",
            "--normal-only",
            help="Only download content that does not require decryption",
            default=False,
            is_flag=True,
        ),
        click.option(
            "-lb",
            "--label",
            help="Filter by label (use helpers.label_helper to process)",
            default=[],
            required=False,
            type=helpers.label_helper,
            callback=lambda ctx, param, value: (
                list(set(itertools.chain.from_iterable(value))) if value else []
            ),
            multiple=True,
        ),
        click.option(
            "-be",
            "--before",
            help="Process posts at or before the given date (MM/DD/YYYY) for likes, unlikes, and downloads",
            type=helpers.arrow_helper,
        ),
        click.option(
            "-af",
            "--after",
            help="Process posts at or after the given date (MM/DD/YYYY) for likes, unlikes, and downloads",
            type=helpers.arrow_helper,
        ),
        click.option(
            "-mt",
            "--mediatype",
            help="Filter by media type (Videos, Audios, Images)",
            default=[],
            required=False,
            type=helpers.mediatype_helper,
            callback=lambda ctx, param, value: (
                list(set(itertools.chain.from_iterable(value))) if value else []
            ),
            multiple=True,
        ),
        click.option(
            "-sx",
            "--size-max",
            help="Filter out files larger than the given size (bytes or human-readable, e.g., 10mb)",
            required=False,
            type=parse_size,
        ),
        click.option(
            "-sm",
            "--size-min",
            help="Filter out files smaller than the given size (bytes or human-readable, e.g., 10mb)",
            required=False,
            type=parse_size,
        ),
        click.option(
            "-mm/-ms",
            "--mass-only/--mass-skip",
            "mass_msg",
            help="Flag for downloading mass content or promos",
            default=None,
            required=False,
        ),
        click.option(
            "-ok/-sk",
            "--only-timed/--skip-timed",
            "timed_only",
            default=None,
            help="Download only promotional or temporary posts",
        ),
    ),
    help="options for posts",
)
@click.option_group(
    "scraper",
    click.option(
        "-u",
        "--usernames",
        "--username",
        help="Select which username to process (name,name2). Set to ALL for all users.",
        default=None,
        type=helpers.username_helper,  # Assuming you'll still use this helper function
        multiple=True,  # Use `multiple=True` for accepting multiple values
        callback=lambda ctx, param, value: (
            list(set(itertools.chain.from_iterable(value))) if value else []
        ),
    ),
    click.option(
        "-eu",
        "--excluded-username",
        help="Select which usernames to exclude (name,name2). Has preference over --username.",
        type=helpers.username_helper,
        default=None,
        multiple=True,
        callback=lambda ctx, param, value: (
            list(set(itertools.chain.from_iterable(value))) if value else []
        ),
    ),
    click.option(
        "-d",
        "--daemon",
        help="Run script in the background. Set value to minimum minutes between script runs. Overdue runs will run as soon as previous run finishes.",
        type=float,
    ),
    click.option(
        "-g",
        "--original",
        help="Don't truncate long paths",
        is_flag=True,  # Use `is_flag=True` for boolean flags
    ),
    click.option(
        "-a",
        "--action",
        help="""
    Select batch action(s) to perform [like,unlike,download].
    Accepts space or comma-separated list. Like and unlike cannot be combined.
    """,
        multiple=True,
        type=helpers.action_helper,
        default=None,
        callback=lambda ctx, param, value: (
            list(set(itertools.chain.from_iterable(value))) if value else []
        ),
    ),
    help="Scraping options",
)
@click.option_group(
    "user filters",
    click.option(
        "-cp",
        "--current-price",
        help="Filter accounts based on either the subscription price, lowest claimable promotional price, or regular price",
        default=None,
        required=False,
        type=click.Choice(["paid", "free"], case_sensitive=False),
        callback=lambda ctx, param, value: value.lower() if value else None,
    ),
    click.option(
        "-rp",
        "--renewal-price",
        help="Filter accounts based on either the lowest claimable promotional price, or regular price",
        default=None,
        required=False,
        type=click.Choice(["paid", "free"], case_sensitive=False),
        callback=lambda ctx, param, value: value.lower() if value else None,
    ),
    click.option(
        "-gp",
        "--regular-price",
        help="Filter accounts based on the regular price",
        default=None,
        required=False,
        type=click.Choice(["paid", "free"], case_sensitive=False),
        callback=lambda ctx, param, value: value.lower() if value else None,
    ),
    click.option(
        "-pp",
        "--promo-price",
        help="Filter accounts based on either the lowest promotional price regardless of claimability, or regular price",
        default=None,
        required=False,
        type=click.Choice(["paid", "free"], case_sensitive=False),
        callback=lambda ctx, param, value: value.lower() if value else None,
    ),
    click.constraints.mutually_exclusive(
        click.option(
            "-lo",
            "--last-seen-only",
            "last_seen",
            help="Filter accounts to ones where last seen is visible",
            default=None,
            required=False,
            is_flag=True,
        ),
        click.option(
            "-ls",
            "--last-seen-skip",
            "last_seen",
            help="Filter accounts to ones where last seen is hidden",
            default=False,
            required=False,
            is_flag=True,
        ),
    ),
    click.option(
        "-fo/-fs",
        "--free-trial-only/--free-trial-skip",
        "free_trail",  # Positional argument for destination attribute
        # help="Filter accounts to only those currently in a free trial (normally paid)",
        # default=None,
        required=False,
        is_flag=True,
        default=None,
    ),
    click.option(
        "-po/-ps",
        "--promo-only/--promo-skip",
        "promo",  # Change dest to be the third element in the list
        help="Filter accounts with any claimable promo price",
        default=None,
        required=False,
        is_flag=True,
        flag_value=True,
    ),
    click.option(
        "-ao",
        "--all-promo-only/--all-promo-skip",
        "all_promo",  # Keep the provided dest
        help="Filter accounts with any promo price",
        default=None,
        required=False,
        is_flag=True,
        flag_value=True,
    ),
    click.option(
        "-ts/-es",
        "--active-subscription/--expired-subscription",
        "sub_status",
        help="Filter accounts to those with non-expired status",
        default=None,
        required=False,
        is_flag=True,
        flag_value=True,
    ),
    click.option(
        "-ro/-rf",
        "--renew-on/--renew-off",
        "renewal",
        help="Filter accounts to those with the renew flag on",
        default=None,
        required=False,
        is_flag=True,
        flag_value=True,
    ),
    click.option(
        "-ul",
        "--user-list",
        help="Filter by userlist. Note: the lists 'ofscraper.main', 'ofscraper.expired', and 'ofscraper.active' are reserved and should not be the name of any list you have on OF",
        default=None,
        multiple=True,
        callback=lambda ctx, param, value: list(
            set(
                itertools.chain.from_iterable(
                    [
                        (
                            re.split(r"[,\s]+", item.lower())
                            if isinstance(item, str)
                            else item
                        )
                        for item in value
                    ]
                )
            )
            if value
            else []
        ),
    ),
    click.option(
        "-bl",
        "--black-list",
        help="Remove all users from selected list. Note: the lists 'ofscraper.main', 'ofscraper.expired', and 'ofscraper.active' are reserved and should not be the name of any list you have on OF",
        default=None,
        multiple=True,
        callback=lambda ctx, param, value: list(
            set(
                itertools.chain.from_iterable(
                    [
                        (
                            re.split(r"[,\s]+", item.lower())
                            if isinstance(item, str)
                            else item
                        )
                        for item in value
                    ]
                )
                if value
                else []
            )
        ),
    ),
    help="Filters out usernames based on selected parameters",
)
@click.option_group(
    "advanced filters",
    click.option(
        "-ppn",
        "--promo-price-min",
        help="Filter accounts where the lowest promo price matches or falls above the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-ppm",
        "--promo-price-max",
        help="Filter accounts where the lowest promo price matches or falls below the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-gpn",
        "--regular-price-min",
        help="Filter accounts where the regular price matches or falls above the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-gpm",
        "--regular-price-max",
        help="Filter accounts where the regular price matches or falls below the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-cpn",
        "--current-price-min",
        help="Filter accounts where the current regular price matches or falls above the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-cpm",
        "--current-price-max",
        help="Filter accounts where the current price matches or falls below the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-rpn",
        "--renewal-price-min",
        help="Filter accounts where the renewal regular price matches or falls above the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-rpm",
        "--renewal-price-max",
        help="Filter accounts where the renewal price matches or falls below the provided value",
        default=None,
        required=False,
        type=int,
    ),
    click.option(
        "-lsb",
        "--last-seen-before",
        help="Filter accounts by last seen being at or before the given date (YYYY-MM-DD format)",
        default=None,
        required=False,
        callback=lambda ctx, param, value: (
            helpers.arrow_helper(value) if value else None
        ),
    ),
    click.option(
        "-lsa",
        "--last-seen-after",
        help="Filter accounts by last seen being at or after the given date (YYYY-MM-DD format)",
        default=None,
        required=False,
        callback=lambda ctx, param, value: (
            helpers.arrow_helper(value) if value else None
        ),
    ),
    click.option(
        "-ea",
        "--expired-after",
        help="Filter accounts by expiration/renewal being at or after the given date (YYYY-MM-DD format)",
        default=None,
        required=False,
        callback=lambda ctx, param, value: (
            helpers.arrow_helper(value) if value else None
        ),
    ),
    click.option(
        "-eb",
        "--expired-before",
        help="Filter accounts by expiration/renewal being at or before the given date (YYYY-MM-DD format)",
        default=None,
        required=False,
        callback=lambda ctx, param, value: (
            helpers.arrow_helper(value) if value else None
        ),
    ),
    click.option(
        "-sa",
        "--subscribed-after",
        help="Filter accounts by subscription date being after the given date (YYYY-MM-DD format)",
        default=None,
        required=False,
        callback=lambda ctx, param, value: (
            helpers.arrow_helper(value) if value else None
        ),
    ),
    click.option(
        "-sb",
        "--subscribed-before",
        help="Filter accounts by sub date being at or before the given date (YYYY-MM-DD format)",
        default=None,
        required=False,
        callback=lambda ctx, param, value: (
            helpers.arrow_helper(value) if value else None
        ),
    ),
    help="Advanced filtering of accounts based on more precise user-defined parameters",
)
@click.option_group(
    "Model Sort",
    click.option(
        "-st",
        "--sort",
        help="What to sort the model list by",
        default="Name",
        type=click.Choice(
            [
                "name",
                "subscribed",
                "expired",
                "current-price",
                "renewal-price",
                "regular-price",
                "promo-price",
                "last-seen",
            ],
            case_sensitive=False,
        ),
        callback=lambda ctx, param, value: value.lower() if value else None,
    ),
    click.option(
        "-ds",
        "--desc",
        help="Sort the model list in descending order",
        is_flag=True,
        default=False,
    ),
    help="Controls the order of the model selection list and the scraping order",
)
@common.common_params
@click.pass_context
def program(ctx, *args, **kwargs):
    return ctx.params, ctx.invoked_subcommand