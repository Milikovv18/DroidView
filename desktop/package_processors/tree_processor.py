


class TreePackageProcessor:

    def convert(self, id, node, level, children):
        #text = node["text"] if "text" in node else node["contentDescription"] if "contentDescription" in node else None
        bounds = f"[{node['w']}x{node['h']}]"
        return TreeItem(id, "text", bounds, None, children)
    
    def get_stats(self):
        return None


class TreeItem:
    id : int
    text : str
    bounds : str
    children : list

    def __init__(self, id, text, bounds, click_callback, children):
        self.id = id
        self.data = text
        self.bounds = bounds
        self.click_callback = click_callback
        self.childItems = children

    def set_parent(self, parent):
        self.parentItem = parent

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0