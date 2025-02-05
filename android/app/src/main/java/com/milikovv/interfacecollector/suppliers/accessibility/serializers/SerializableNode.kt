package com.milikovv.interfacecollector.suppliers.accessibility.serializers

import kotlinx.serialization.Serializable

@Serializable
sealed class SerializableNode {
    var children: ArrayList<SerializableNode> = ArrayList()
}

@Serializable
data class VisualizableNode(
    val x : Int,
    val y : Int,
    val w : Int,
    val h : Int
) : SerializableNode()

@Serializable
data class DescriptiveNode(
    // Masked booleans
    val booleans : Int,
    // Text
    val className : String?,
    val containerTitle : String? = null,
    val contentDescription : String? = null,
    val errorText : String? = null,
    val hintText : String? = null,
    val tooltipText : String? = null,
    val packageName : String,
    val paneTitle : String? = null,
    val stateDescription : String? = null,
    val text : String? = null,
    val uniqueId : String? = null,
    val viewIdResourceName : String? = null,
    // Numbers
    val drawingOrder : Int,
    val inputType : Int,
    // Misc
    val x : Int,
    val y : Int,
    val w : Int,
    val h : Int,
    val actionList : List<Long>
) : SerializableNode()

data class BooleanValues(
    val canOpenPopup : Boolean,
    val isDataSensitive : Boolean,
    val isAccessibilityFocused : Boolean,
    val isCheckable : Boolean,
    val isChecked : Boolean,
    val isClickable : Boolean,
    val isContentInvalid : Boolean,
    val isContextClickable : Boolean,
    val isDismissable : Boolean,
    val isEditable : Boolean,
    val isEnabled : Boolean,
    val isFocusable : Boolean,
    val isFocused : Boolean,
    val isHeading : Boolean,
    val isImportantForAccessibility : Boolean,
    val isLongClickable : Boolean,
    val isMultiline : Boolean,
    val isPassword : Boolean,
    val isScreenReaderFocusable : Boolean,
    val isScrollable : Boolean,
    val isSelected : Boolean,
    val isShowingHintText : Boolean,
    val isTextEntryKey : Boolean,
    val isTextSelectable : Boolean,
    val isVisibleToUser : Boolean,
)