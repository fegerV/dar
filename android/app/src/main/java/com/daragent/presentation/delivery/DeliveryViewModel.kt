package com.daragent.presentation.delivery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.domain.model.Delivery
import com.daragent.domain.repository.DeliveryRepository
import com.daragent.di.ServiceLocator
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class DeliveryState(
    val delivery: Delivery? = null,
    val progress: Int = 0,
    val status: String = "pending",
    val publicUrl: String? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class DeliveryViewModel(
    private val deliveryRepository: DeliveryRepository? = null
) : ViewModel() {
    private val repo = deliveryRepository ?: ServiceLocator.projectRepository as? DeliveryRepository ?: ServiceLocator.projectRepository
    private val _state = MutableStateFlow(DeliveryState())
    val state: StateFlow<DeliveryState> = _state

    fun startTracking(projectId: String) {
        _state.value = _state.value.copy(isLoading = true, status = "tracking")
        viewModelScope.launch {
            kotlinx.coroutines.delay(2000)
            val fake = Delivery(
                id = "delivery_$projectId",
                projectId = projectId,
                channel = "link",
                status = "sent",
                destination = null,
                publicUrl = "https://daragent.ru/share/delivery_$projectId",
                createdAt = "",
                scheduledAt = null,
                sentAt = null,
                openedAt = null
            )
            _state.value = _state.value.copy(
                delivery = fake,
                status = fake.status,
                publicUrl = fake.publicUrl,
                progress = 100,
                isLoading = false
            )
        }
    }
}
