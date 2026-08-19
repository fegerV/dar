package com.daragent.presentation.mascot

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class MascotRepository @Inject constructor() {
    private val _currentState = MutableStateFlow<MascotState>(MascotState.Idle)
    val currentState: StateFlow<MascotState> = _currentState.asStateFlow()

    private val _bubbleContent = MutableStateFlow<MascotBubbleContent?>(null)
    val bubbleContent: StateFlow<MascotBubbleContent?> = _bubbleContent.asStateFlow()

    fun handleEvent(event: MascotEvent, bubbleText: String? = null) {
        val newState = MascotState.fromEvent(event)
        val current = _currentState.value

        if (newState.isLoop && current == newState) {
            return
        }

        _currentState.value = newState

        if (bubbleText != null) {
            _bubbleContent.value = MascotBubbleContent(text = bubbleText)
        }
    }

    fun setState(state: MascotState, bubbleText: String? = null) {
        _currentState.value = state

        if (bubbleText != null) {
            _bubbleContent.value = MascotBubbleContent(text = bubbleText)
        }
    }

    fun clearBubble() {
        _bubbleContent.value = null
    }

    fun getTransitionPath(from: MascotState, to: MascotState): List<MascotState> {
        if (from == to) return listOf(to)

        val path = mutableListOf<MascotState>()

        val oneShotStates = setOf(
            MascotState.Hello,
            MascotState.Write,
            MascotState.Read,
            MascotState.LookUp,
            MascotState.Happy,
            MascotState.Surprised,
            MascotState.Wink,
            MascotState.Point,
            MascotState.Celebrate,
            MascotState.Success,
            MascotState.Error,
            MascotState.Sorry,
            MascotState.Goodbye,
        )

        if (from in oneShotStates) {
            val fallback = from.fallbackState ?: MascotState.Idle
            path.add(fallback)
        }

        path.add(to)
        return path
    }

    fun reset() {
        _currentState.value = MascotState.Idle
        _bubbleContent.value = null
    }
}
