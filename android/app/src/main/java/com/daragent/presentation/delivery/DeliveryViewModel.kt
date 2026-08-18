package com.daragent.presentation.delivery

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.di.ServiceLocator
import com.daragent.domain.model.Delivery
import com.daragent.domain.repository.DeliveryRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class DeliveryState(
    val delivery: Delivery? = null,
    val deliveries: List<Delivery> = emptyList(),
    val progress: Int = 0,
    val status: String = "pending",
    val publicUrl: String? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

class DeliveryViewModel(
    deliveryRepository: DeliveryRepository? = null
) : ViewModel() {
    private val repo = deliveryRepository ?: ServiceLocator.deliveryRepository
    private val _state = MutableStateFlow(DeliveryState())
    val state: StateFlow<DeliveryState> = _state

    fun startTracking(projectId: String) {
        _state.value = _state.value.copy(isLoading = true, status = "tracking")
        viewModelScope.launch {
            val result = repo.getByProject(projectId)
            result.onSuccess { deliveries ->
                val delivery = deliveries.lastOrNull()
                _state.value = _state.value.copy(
                    deliveries = deliveries,
                    delivery = delivery,
                    status = delivery?.status ?: "pending",
                    publicUrl = delivery?.publicUrl,
                    progress = if (delivery?.status == "sent") 100 else 50,
                    isLoading = false
                )
            }.onFailure { e ->
                _state.value = _state.value.copy(
                    status = "error",
                    error = e.message,
                    isLoading = false
                )
            }
        }
    }
}
