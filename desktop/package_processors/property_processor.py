from dataclasses import dataclass


class PropertyPackageProcessor:

    def convert(self, id, node, level, children):
        # Simple package completeness check
        if "booleans" not in node:
            return PropertiesLayout(id, [], f"[{node['w']}x{node['h']}]", *(40 * [None]))

        bools = node["booleans"]
        return PropertiesLayout(
            id,
            children,
            self.safe_string_extractor(node, "boundsInScreen"),

            self.safe_string_extractor(node, "className"),
            self.safe_string_extractor(node, "containerTitle"),
            self.safe_string_extractor(node, "contentDescription"),
            self.safe_string_extractor(node, "errorText"),
            self.safe_string_extractor(node, "hintText"),
            self.safe_string_extractor(node, "tooltipText"),
            self.safe_string_extractor(node, "packageName"),
            self.safe_string_extractor(node, "paneTitle"),
            self.safe_string_extractor(node, "stateDescription"),
            self.safe_string_extractor(node, "text"),
            self.safe_string_extractor(node, "uniqueId"),
            self.safe_string_extractor(node, "viewIdResourceName"),
            # Numbers
            self.safe_string_extractor(node, "drawingOrder"),
            self.safe_string_extractor(node, "inputType"),
            # Misc
            self.safe_string_extractor(node, "actionList"),
            # Booleans
            self.bool_extractor(bools, 2**0),
            self.bool_extractor(bools, 2**1),
            self.bool_extractor(bools, 2**2),
            self.bool_extractor(bools, 2**3),
            self.bool_extractor(bools, 2**4),
            self.bool_extractor(bools, 2**5),
            self.bool_extractor(bools, 2**6),
            self.bool_extractor(bools, 2**7),
            self.bool_extractor(bools, 2**8),
            self.bool_extractor(bools, 2**9),
            self.bool_extractor(bools, 2**10),
            self.bool_extractor(bools, 2**11),
            self.bool_extractor(bools, 2**12),
            self.bool_extractor(bools, 2**13),
            self.bool_extractor(bools, 2**14),
            self.bool_extractor(bools, 2**15),
            self.bool_extractor(bools, 2**16),
            self.bool_extractor(bools, 2**17),
            self.bool_extractor(bools, 2**18),
            self.bool_extractor(bools, 2**19),
            self.bool_extractor(bools, 2**20),
            self.bool_extractor(bools, 2**21),
            self.bool_extractor(bools, 2**22),
            self.bool_extractor(bools, 2**23),
            self.bool_extractor(bools, 2**24),
        )
    
    def safe_string_extractor(self, node, prop):
        return node[prop] if prop in node else "Null"
    
    def bool_extractor(self, bools : int, offset : int):
        return bool(bools & offset)
    
    def get_stats(self):
        return None


@dataclass
class PropertiesLayout:
    id : int
    children : list
    boundsInScreen : str

    className : str
    containerTitle : str
    contentDescription : str
    errorText : str
    hintText : str
    tooltipText : str
    packageName : str
    paneTitle : str
    stateDescription : str
    text : str
    uniqueId : str
    viewIdResourceName : str
    # Numbers
    drawingOrder : int
    inputType : int
    # Misc
    actionList : list
    # Booleans
    canOpenPopup : bool
    isDataSensitive : bool
    isAccessibilityFocused : bool
    isCheckable : bool
    isChecked : bool
    isClickable : bool
    isContentInvalid : bool
    isContextClickable : bool
    isDismissable : bool
    isEditable : bool
    isEnabled : bool
    isFocusable : bool
    isFocused : bool
    isHeading : bool
    isImportantForAccessibility : bool
    isLongClickable : bool
    isMultiline : bool
    isPassword : bool
    isScreenReaderFocusable : bool
    isScrollable : bool
    isSelected : bool
    isShowingHintText : bool
    isTextEntryKey : bool
    isTextSelectable : bool
    isVisibleToUser : bool
