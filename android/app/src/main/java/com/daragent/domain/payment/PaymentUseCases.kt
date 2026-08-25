package com.daragent.domain.payment

import com.daragent.data.payment.PaymentRepository
import com.daragent.data.payment.PaymentCreationResult
import com.daragent.core.network.model.PaymentDto
import javax.inject.Inject

class CreatePaymentUseCase @Inject constructor(
    private val paymentRepository: PaymentRepository,
) {
    suspend operator fun invoke(amount: Double, currency: String): Result<PaymentCreationResult> {
        return paymentRepository.createPayment(amount, currency)
    }
}

class GetPaymentStatusUseCase @Inject constructor(
    private val paymentRepository: PaymentRepository,
) {
    suspend operator fun invoke(paymentId: String): Result<PaymentDto> {
        return paymentRepository.getPayment(paymentId)
    }
}

class GetPaymentsUseCase @Inject constructor(
    private val paymentRepository: PaymentRepository,
) {
    suspend operator fun invoke(): Result<List<PaymentDto>> {
        return paymentRepository.getPayments()
    }
}
