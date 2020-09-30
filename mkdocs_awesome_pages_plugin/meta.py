import yaml
from typing import Optional, List, Union


class DuplicateRestTokenError(Exception):
    def __init__(self, context: str):
        super().__init__('Rest token "..." is only allowed once [{context}]'.format(context=context))


class MetaNavItem:

    def __init__(self, value: str, title: Optional[str] = None):
        self.value = value
        self.title = title

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetaNavItem) and self.value == other.value and self.title == other.title

    @staticmethod
    def from_yaml(item: Union[str, dict], context: str):
        if isinstance(item, str):
            return MetaNavItem(item)

        if isinstance(item, dict) and len(item) == 1:
            (title, value) = list(item.items())[0]
            if isinstance(value, str) and isinstance(title, str):
                return MetaNavItem(value, title)

        raise TypeError('Invalid nav item format {type} [{context}]'.format(type=item, context=context))


class Meta:

    TITLE_ATTRIBUTE = 'title'
    NAV_ATTRIBUTE = 'nav'
    NAV_REST_TOKEN = MetaNavItem('...')
    ARRANGE_ATTRIBUTE = 'arrange'
    ARRANGE_REST_TOKEN = '...'
    COLLAPSE_ATTRIBUTE = 'collapse'
    COLLAPSE_SINGLE_PAGES_ATTRIBUTE = 'collapse_single_pages'
    HIDE_ATTRIBUTE = 'hide'

    def __init__(self, *, title: Optional[str] = None, arrange: Optional[List[str]] = None,
                 nav: Optional[List[MetaNavItem]] = None, path: Optional[str] = None, collapse: bool = None,
                 collapse_single_pages: bool = None, hide: bool = None):

        if nav is None and arrange is not None:
            nav = [MetaNavItem(value) for value in arrange]
            if Meta.NAV_REST_TOKEN not in nav:
                nav.append(Meta.NAV_REST_TOKEN)

        self.title = title
        self.nav = nav
        self.path = path
        self.collapse = collapse
        self.collapse_single_pages = collapse_single_pages
        self.hide = hide

    @staticmethod
    def try_load_from(path: Optional[str]) -> 'Meta':
        if path is None:
            return Meta()
        try:
            return Meta.load_from(path)
        except FileNotFoundError:
            return Meta(path=path)

    @staticmethod
    def load_from(path: str) -> 'Meta':
        with open(path, encoding='utf-8') as file:
            contents = yaml.safe_load(file) or {}
            title = contents.get(Meta.TITLE_ATTRIBUTE)
            arrange = contents.get(Meta.ARRANGE_ATTRIBUTE)
            nav = contents.get(Meta.NAV_ATTRIBUTE)
            collapse = contents.get(Meta.COLLAPSE_ATTRIBUTE)
            collapse_single_pages = contents.get(Meta.COLLAPSE_SINGLE_PAGES_ATTRIBUTE)
            hide = contents.get(Meta.HIDE_ATTRIBUTE)

            if title is not None:
                if not isinstance(title, str):
                    raise TypeError(
                        'Expected "{attribute}" attribute to be a string - got {type} [{context}]'
                        .format(attribute=Meta.TITLE_ATTRIBUTE,
                                type=type(title),
                                context=path)
                    )
            if arrange is not None:
                if not isinstance(arrange, list) or not all(isinstance(s, str) for s in arrange):
                    raise TypeError(
                        'Expected "{attribute}" attribute to be a list of strings - got {type} [{context}]'
                        .format(attribute=Meta.ARRANGE_ATTRIBUTE,
                                type=type(arrange),
                                context=path)
                    )
                if arrange.count(Meta.ARRANGE_REST_TOKEN) > 1:
                    raise DuplicateRestTokenError(path)

            if nav is not None:
                if not isinstance(nav, list):
                    raise TypeError(
                        'Expected "{attribute}" attribute to be a list - got {type} [{context}]'
                        .format(attribute=Meta.NAV_ATTRIBUTE,
                                type=type(nav),
                                context=path)
                    )

                nav = [MetaNavItem.from_yaml(item, path) for item in nav]

                if nav.count(Meta.NAV_REST_TOKEN) > 1:
                    raise DuplicateRestTokenError(path)

            if collapse is not None:
                if not isinstance(collapse, bool):
                    raise TypeError(
                        'Expected "{attribute}" attribute to be a boolean - got {type} [{context}]'
                        .format(attribute=Meta.COLLAPSE_ATTRIBUTE,
                                type=type(collapse),
                                context=path)
                    )
            if collapse_single_pages is not None:
                if not isinstance(collapse_single_pages, bool):
                    raise TypeError(
                        'Expected "{attribute}" attribute to be a boolean - got {type} [{context}]'
                        .format(attribute=Meta.COLLAPSE_SINGLE_PAGES_ATTRIBUTE,
                                type=type(collapse_single_pages),
                                context=path)
                    )
            if hide is not None:
                if not isinstance(hide, bool):
                    raise TypeError(
                        'Expected "{attribute}" attribute to be a boolean - got {type} [{context}]'
                        .format(attribute=Meta.COLLAPSE_ATTRIBUTE,
                                type=type(hide),
                                context=path)
                    )

            return Meta(title=title, arrange=arrange, nav=nav, path=path,
                        collapse=collapse, collapse_single_pages=collapse_single_pages, hide=hide)
