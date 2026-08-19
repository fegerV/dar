package com.daragent.presentation.mascot

import androidx.annotation.DrawableRes
import androidx.annotation.RawRes

sealed class MascotState(
    val riveStateName: String,
    val isLoop: Boolean,
    val fallbackState: MascotState? = MascotState.Idle,
) {
    data object Idle : MascotState("idle", true)
    data object Hello : MascotState("hello", false, Idle)
    data object Listen : MascotState("listen", true)
    data object Think : MascotState("think", true)
    data object Write : MascotState("write", false, Happy)
    data object Read : MascotState("read", false, Idle)
    data object LookUp : MascotState("look_up", false, Idle)
    data object Happy : MascotState("happy", false, Idle)
    data object Surprised : MascotState("surprised", false, Idle)
    data object Wink : MascotState("wink", false, Idle)
    data object Point : MascotState("point", false, Idle)
    data object Celebrate : MascotState("celebrate", false, Happy)
    data object Working : MascotState("working", true)
    data object Success : MascotState("success", false, Happy)
    data object Error : MascotState("error", false, Sorry)
    data object Sorry : MascotState("sorry", false, Idle)
    data object Goodbye : MascotState("goodbye", false, Idle)

    companion object {
        val allStates: List<MascotState> = listOf(
            Idle, Hello, Listen, Think, Write, Read, LookUp, Happy,
            Surprised, Wink, Point, Celebrate, Working, Success,
            Error, Sorry, Goodbye,
        )

        fun fromEvent(event: MascotEvent): MascotState {
            return when (event) {
                MascotEvent.SHOW_HELLO -> Hello
                MascotEvent.USER_TYPING -> Listen
                MascotEvent.USER_FINISHED_TYPING -> Think
                MascotEvent.ANSWER_RECEIVED -> Think
                MascotEvent.SAVE_STARTED -> Write
                MascotEvent.SAVE_COMPLETED -> Happy
                MascotEvent.INTERESTING_FACT -> Surprised
                MascotEvent.GENERATION_STARTED -> Working
                MascotEvent.GENERATION_COMPLETED -> Celebrate
                MascotEvent.GENERATION_FAILED -> Error
                MascotEvent.USER_SELECTED_TEMPLATE -> Point
                MascotEvent.USER_SELECTED_PREMIUM -> Wink
                MascotEvent.SHARE_COMPLETED -> Celebrate
                MascotEvent.REFERRAL_COMPLETED -> Happy
            }
        }
    }
}

enum class MascotEvent {
    SHOW_HELLO,
    USER_TYPING,
    USER_FINISHED_TYPING,
    ANSWER_RECEIVED,
    SAVE_STARTED,
    SAVE_COMPLETED,
    INTERESTING_FACT,
    GENERATION_STARTED,
    GENERATION_COMPLETED,
    GENERATION_FAILED,
    USER_SELECTED_TEMPLATE,
    USER_SELECTED_PREMIUM,
    SHARE_COMPLETED,
    REFERRAL_COMPLETED,
}

data class MascotBubbleContent(
    @DrawableRes val iconRes: Int? = null,
    val text: String? = null,
    val typingText: String? = null,
)
