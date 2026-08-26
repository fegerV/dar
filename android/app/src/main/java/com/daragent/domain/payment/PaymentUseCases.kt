package com.daragent.domain.payment

import com.daragent.domain.model.Payment
import com.daragent.domain.repository.PaymentRepository
import javax.inject.Inject

class CreatePaymentUseCase @Inject constructor(
    private val paymentRepository: PaymentRepository,
) {
    suspend operator fun invoke(projectId: String, method: String = "yookassa"): Result<Payment> {
        return paymentRepository.createPayment(projectId, method)
    }
}

class GetPaymentStatusUseCase @Inject constructor(
    private val paymentRepository: PaymentRepository,
) {
    suspend operator fun invoke(paymentId: String): Result<Payment> {
        return paymentRepository.getPaymentStatus(paymentId)
    }
}

class GetPaymentsUseCase @Inject constructor(
    private val paymentRepository: PaymentRepository,
) {
    suspend operator fun invoke(): Result<List<Payment>> {
        return paymentRepository.listPayments()
    }
}
