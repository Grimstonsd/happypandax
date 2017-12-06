__pragma__('alias', 'as_', 'as')
from src.react_utils import (h,
                             e,
                             React,
                             createReactClass,
                             Link)
from src.ui import ui, Slider
from src.i18n import tr
from src.state import state
from src.client import ItemType, ViewType, ImageSize, client
from src.single import galleryitem, thumbitem, artistitem
from src.views import itemview, tagview
from src import utils


def get_config(data=None, error=None):
    if data is not None and not error:
        this.setState({"external_viewer": data['this.use_external_image_viewer']})
    elif error:
        state.app.notif("Failed to fetch config: {}".format(error), level="error")
    else:
        return
        client.call_func(
            "get_config", this.get_config, cfg={
                'this.use_external_image_viewer': this.state.external_viewer})


def get_item(data=None, error=None):
    if data is not None and not error:
        this.setState({"data": data,
                       "loading": False,
                       "rating": data.rating,
                       'loading_group': True,
                       })
        if data.metatags.favorite:
            this.setState({"fav": 1})
        if data.grouping_id:
            client.call_func("get_related_items", this.get_grouping,
                             item_type=ItemType.Grouping,
                             related_type=this.state.item_type,
                             item_id=data.grouping_id)
            client.call_func("get_related_items", this.get_status,
                             item_type=ItemType.Grouping,
                             related_type=ItemType.Status,
                             item_id=data.grouping_id)
        if data.language_id:
            client.call_func("get_item", this.get_lang,
                             item_type=ItemType.Language,
                             item_id=data.language_id)
    elif error:
        state.app.notif("Failed to fetch item ({})".format(this.state.id), level="error")
    else:
        item = this.state.item_type
        item_id = this.state.id
        if item and item_id:
            client.call_func("get_item", this.get_item, item_type=item, item_id=item_id)
            this.setState({'loading': True})


def get_grouping(data=None, error=None):
    if data is not None and not error:
        this.setState({"group_data": data, "loading_group": False})
    elif error:
        state.app.notif("Failed to fetch grouping ({})".format(this.state.id), level="error")


def get_lang(data=None, error=None):
    if data is not None and not error:
        this.setState({"lang_data": data})
    elif error:
        state.app.notif("Failed to fetch language ({})".format(this.state.id), level="error")

__pragma__("tconv")


def get_status(data=None, error=None):
    if data is not None and not error:
        if data:
            this.setState({"status_data": data[0]})
    elif error:
        state.app.notif("Failed to fetch status ({})".format(this.state.id), level="error")
__pragma__("notconv")


def toggle_external_viewer(e, d):
    v = not d.active
    this.setState({'external_viewer': v})
    utils.storage.set('external_viewer', v)

__pragma__("tconv")


def open_external():
    if this.state.data:
        client.call_func("open_gallery", None, item_id=this.state.data.id, item_type=this.state.item_type)
__pragma__("notconv")

def gallery_on_update(p_props, p_state):
    if p_props.location.search != this.props.location.search:
        this.setState({'id': int(utils.get_query("id", 0))})

    if any((
        p_state.id != this.state.id,
    )):
        this.get_item()

__pragma__("tconv")


def page_render():

    fav = this.state.fav
    title = ""
    rating = this.state.rating
    artists = []
    item_id = this.state.id
    info = ""
    inbox = False
    trash = False
    read_count = 0
    date_pub = "Unknown"
    date_upd = "Unknown"
    date_read = "Unknown"
    date_added = "Unknown"
    urls = []
    parodies = []
    circles = []
    if this.state.data:
        item_id = this.state.data.id
        parodies = this.state.data.parodies

        if this.state.data.pub_date:
            date_pub = utils.moment.unix(this.state.data.pub_date).format("LL")
            date_pub += " (" + utils.moment.unix(this.state.data.pub_date).fromNow() + ")"
        if this.state.data.last_updated:
            date_upd = utils.moment.unix(this.state.data.last_updated).format("LLL")
            date_upd += " (" + utils.moment.unix(this.state.data.last_updated).fromNow() + ")"
        if this.state.data.last_read:
            date_read = utils.moment.unix(this.state.data.last_read).format("LLL")
            date_read += " (" + utils.moment.unix(this.state.data.last_read).fromNow() + ")"
        if this.state.data.timestamp:
            date_added = utils.moment.unix(this.state.data.timestamp).format("LLL")
            date_added += " (" + utils.moment.unix(this.state.data.timestamp).fromNow() + ")"
        read_count = this.state.data.times_read
        info = this.state.data.info
        title = this.state.data.titles[0].js_name
        inbox = this.state.data.metatags.inbox
        trash = this.state.data.metatags.trash
        if not item_id:
            item_id = this.state.data.id

        artists = this.state.data.artists

        for u in this.state.data.urls:
            urls.append(u.js_name)

    series_data = []
    if this.state.group_data:
        series_data = this.state.group_data

    status = this.state.status_data.js_name if this.state.status_data.js_name else "Unknown"

    rows = []

    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, info, as_="h5"), colSpan="2")))
    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Artist(s):", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, *(e(artistitem.ArtistLabel, data=x) for x in artists))))
    if circles:
        rows.append(e(ui.Table.Row,
                      e(ui.Table.Cell, e(ui.Header, "Circle(s):", as_="h5"), collapsing=True),
                      e(ui.Table.Cell, *(e("span", x.js_name) for x in circles))))
    if parodies:
        rows.append(e(ui.Table.Row,
                      e(ui.Table.Cell, e(ui.Header, "Parody:", as_="h5"), collapsing=True),
                      e(ui.Table.Cell,)))
    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Language:", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, this.state.lang_data.js_name)))
    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Status:", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, e(ui.Label, tr(this, "general.db-status-{}".format(status.lower()), status), color={"completed": "green", "ongoing": "orange", "unknown": "grey"}.get(status.lower(), "blue")))))
    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Published:", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, e(ui.Label, date_pub))))
    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Times read:", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, e(ui.Label, read_count, circular=True))))
    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Rating:", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, e(ui.Rating, icon="star", rating=rating, maxRating=10, size="huge", clearable=True))))

    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "Tags:", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, e(tagview.TagView, item_id=item_id, item_type=this.state.item_type))))

    rows.append(e(ui.Table.Row,
                  e(ui.Table.Cell, e(ui.Header, "URL(s):", as_="h5"), collapsing=True),
                  e(ui.Table.Cell, e(ui.List, *[e(ui.List.Item, h("span", h("a", x, href=x, target="_blank"), e(ui.List.Icon, js_name="external share"))) for x in urls]))))

    indicators = []

    if inbox:
        indicators.append(e(ui.Icon, js_name="inbox", size="big", title="This gallery is in your inbox"))

    if trash:
        indicators.append(e(ui.Icon, js_name="trash", color="red", size="big",
                            title="This gallery is set to be deleted"))

    buttons = []
    external_view = []
    if utils.is_same_machine():
        external_view.append(e(ui.Button, icon="external", toggle=True, active=this.state.external_viewer,
                               title="Open in external viewer", onClick=this.toggle_external_viewer))

    if this.state.external_viewer:
        read_btn = {'onClick': this.open_external}
    else:
        read_btn = {'as': Link, 'to': utils.build_url(
            "/item/page", {'gid': item_id}, keep_query=False)}

    buttons.append(
        e(ui.Grid.Row,
          e(ui.Grid.Column,
            e(ui.Button.Group,
              e(ui.Button, e(ui.Icon, js_name="history"), "Save for later"),
              e(ui.Button.Or, text="or"),
              e(ui.Button, "Read", primary=True, **read_btn),
              *external_view,
              ),
            textAlign="center",
            ),
          centered=True,
          ))

    if inbox:
        buttons.append(
            e(ui.Grid.Row,
              e(ui.Grid.Column,
                e(ui.Button,
                    e(ui.Icon, js_name="grid layout"), "Send to Library", color="green"),
                textAlign="center",
                ),
              centered=True,
              ))
    buttons.append(
        e(ui.Grid.Row,
          e(ui.Grid.Column,
            e(ui.Button,
              e(ui.Icon, js_name="trash" if not trash else "reply"),
              "Send to Trash" if not trash else "Restore",
              color="red" if not trash else "grey"),
            textAlign="center",
            ),
          centered=True,
          ))

    if trash:
        buttons.append(
            e(ui.Grid.Row,
              e(ui.Grid.Column,
                e(ui.Button.Group,
                  e(ui.Button,
                    e(ui.Icon, js_name="close"), "Delete", color="red"),
                  e(ui.Button, icon="remove circle outline", toggle=True, active=this.state.delete_files,
                    title="Delete files"),
                  e(ui.Button, icon="recycle", toggle=True, active=this.state.send_to_recycle,
                    title="Send files to Recycle Bin")
                  ),
                textAlign="center",
                ),
              centered=True,
              ))

    pages_cfg = e(itemview.ItemViewConfig,
                  onSubmit=this.toggle_pages_config,
                  visible=this.state.visible_page_cfg
                  )

    return e(ui.Grid,
             e(ui.Grid.Row, e(ui.Grid.Column, e(ui.Breadcrumb, icon="right arrow",))),
             e(ui.Grid.Row,
                 e(ui.Grid.Column,
                   e(ui.Grid, e(ui.Grid.Row,
                                e(ui.Grid.Column,
                                  e(thumbitem.Thumbnail,
                                    size_type=ImageSize.Big,
                                    item_type=this.state.item_type,
                                    item_id=item_id,
                                    size="medium",
                                    shape="rounded",
                                    bordered=True,),
                                    tablet=10, mobile=6,
                                  ),
                                centered=True,
                                ),
                     *buttons,
                     centered=True, verticalAlign="top"),
                   ),
                 e(ui.Grid.Column,
                   e(ui.Grid,
                       e(ui.Grid.Row,
                           e(ui.Grid.Column, e(ui.Rating, icon="heart", size="massive", rating=fav), floated="right",),
                           e(ui.Grid.Column, *indicators, floated="right", textAlign="right"),
                         columns=2,
                         ),
                       e(ui.Grid.Row,
                         e(ui.Grid,
                           e(ui.Grid.Row, e(ui.Grid.Column, e(ui.Header, title, as_="h3"), textAlign="center")),
                           e(ui.Grid.Row,
                             e(ui.Grid.Column,
                               e(ui.Table,
                                 e(ui.Table.Body,
                                   *rows
                                   ),
                                 basic="very"
                                 ))),
                           stackable=True,
                           padded=False,
                           relaxed=True,
                           ),
                         ),
                     divided="vertically",
                     ),
                   ),
                 columns=2,
                 as_=ui.Segment,
                 # loading=this.state.loading,
                 basic=True,
               ),
             e(ui.Grid.Row,
                 e(ui.Grid.Column, e(ui.Label, "Date added", e(ui.Label.Detail, date_added))),
                 e(ui.Grid.Column, e(ui.Label, "Last read", e(ui.Label.Detail, date_read))),
                 e(ui.Grid.Column, e(ui.Label, "Last updated", e(ui.Label.Detail, date_upd))),
                 columns=3
               ),
             e(ui.Grid.Row, e(ui.Grid.Column,
                              e(Slider, *[e(galleryitem.Gallery, data=x) for x in series_data],
                                loading=this.state.loading_group,
                                secondary=True,
                                sildesToShow=4,
                                label="Series"),
                              )),
             e(ui.Grid.Row, e(ui.Grid.Column, e(itemview.ItemView,
                                                item_id=item_id,
                                                item_type=ItemType.Gallery,
                                                related_type=ItemType.Page,
                                                view_filter=None,
                                                label="Pages",
                                                config_el=pages_cfg,
                                                toggle_config=this.toggle_pages_config,
                                                external_viewer=this.state.external_viewer,
                                                container=True, secondary=True))),
             stackable=True,
             container=True,
             )
__pragma__("notconv")


Page = createReactClass({
    'displayName': 'GalleryPage',

    'getInitialState': lambda: {'id': int(utils.get_query("id", 0)),
                                'data': this.props.data,
                                'rating': 0,
                                'fav': 0,
                                'lang_data': this.props.lang_data or {},
                                'status_data': this.props.status_data or {},
                                'group_data': this.props.group_data or [],
                                'item_type': ItemType.Gallery,
                                'loading': True,
                                'loading_group': True,
                                'external_viewer': utils.storage.get("external_viewer", False),
                                'send_to_recycle': True,
                                'delete_files': False,
                                'visible_page_cfg': False,
                                },

    'on_read': lambda: utils.go_to(this.props.history, "/item/page", {'gid': this.state.data.id}, keep_query=False),
    'get_item': get_item,
    'get_grouping': get_grouping,
    'get_lang': get_lang,
    'get_status': get_status,
    'get_config': get_config,
    'open_external': open_external,

    'toggle_pages_config': lambda a: this.setState({'visible_page_cfg': not this.state.visible_page_cfg}),
    'toggle_external_viewer': toggle_external_viewer,

    'componentWillMount': lambda: all((this.props.menu([e(ui.Menu.Menu, e(ui.Menu.Item, e(ui.Icon, js_name="edit"), "Edit"), position="right")]),
                                       (this.get_item() if not this.state.data else None),
                                       this.get_config(),
                                       )),
    'componentDidUpdate': gallery_on_update,

    'render': page_render
})
