from application.models import MarqueeTexts


def marquee_context_processor(request):
   obj = MarqueeTexts.objects.first()
   return {'marqueeText':obj.text} 