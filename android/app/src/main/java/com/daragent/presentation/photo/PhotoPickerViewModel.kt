package com.daragent.presentation.photo

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.daragent.core.network.api.MediaApi
import com.daragent.core.network.model.UploadResponse
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.InputStream
import javax.inject.Inject

data class PhotoPickerUiState(
    val selectedUri: Uri? = null,
    val isUploading: Boolean = false,
    val uploadProgress: Int = 0,
    val uploadedUrl: String? = null,
    val error: String? = null,
    val qualityScore: Float? = null,
    val qualityIssues: List<String> = emptyList(),
)

@HiltViewModel
class PhotoPickerViewModel @Inject constructor(
    private val mediaApi: MediaApi,
) : ViewModel() {

    private val _uiState = MutableStateFlow(PhotoPickerUiState())
    val uiState: StateFlow<PhotoPickerUiState> = _uiState.asStateFlow()

    fun onPhotoSelected(uri: Uri) {
        _uiState.update {
            it.copy(
                selectedUri = uri,
                uploadedUrl = null,
                error = null,
                qualityScore = null,
                qualityIssues = emptyList(),
            )
        }
    }

    fun uploadPhoto(contentResolver: android.content.ContentResolver) {
        val uri = _uiState.value.selectedUri ?: return

        viewModelScope.launch {
            _uiState.update { it.copy(isUploading = true, uploadProgress = 0, error = null) }

            try {
                val inputStream: InputStream = contentResolver.openInputStream(uri)
                    ?: throw Exception("Cannot open file")

                val bytes = inputStream.readBytes()
                inputStream.close()

                val requestBody = bytes.toRequestBody("image/*".toMediaTypeOrNull())
                val part = MultipartBody.Part.createFormData(
                    "file",
                    "photo.jpg",
                    requestBody,
                )

                val result = uploadToServer(part)

                _uiState.update {
                    it.copy(
                        isUploading = false,
                        uploadProgress = 100,
                        uploadedUrl = result.url,
                        qualityScore = 0.85f,
                        qualityIssues = emptyList(),
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isUploading = false,
                        error = e.message ?: "Upload failed",
                    )
                }
            }
        }
    }

    private suspend fun uploadToServer(part: MultipartBody.Part): UploadResponse {
        val response = mediaApi.uploadPhoto(part)
        if (response.isSuccessful) {
            return response.body() ?: throw Exception("Empty response")
        } else {
            throw Exception("Upload failed: ${response.code()}")
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }

    fun reset() {
        _uiState.update { PhotoPickerUiState() }
    }
}
